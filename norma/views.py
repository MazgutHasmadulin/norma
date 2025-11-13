from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Proj, Cases, Launches, TestRunResult
from .forms import ProjCreationForm, CaseCreationForm, LaunchCreationForm, TestResultUpdateForm
from django.db.models import Prefetch
from django.urls import reverse

# --- Проекты ---
def proj_list(request):
    all_projs = Proj.objects.filter(last_update_date__lte=timezone.now()).order_by('-last_update_date')
    paginator = Paginator(all_projs, 10)  # 10 проектов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'norma/proj_list.html', {'page_obj': page_obj, 'projs': page_obj.object_list})

def proj_dashboard(request, pk):
    project = get_object_or_404(Proj, pk=pk)
    launches = Launches.objects.filter(project=project).order_by('-created_date')
    
    # Подсчет статусов кейсов
    all_cases = Cases.objects.filter(project=project)
    total_cases = all_cases.count()
    
    draft_cases = all_cases.filter(status='draft').count()
    review_cases = all_cases.filter(status='on_review').count()
    actual_cases = all_cases.filter(status='actual').count()
    correction_cases = all_cases.filter(status='correction_needed').count()
    
    # Вычисление процентов
    def get_percentage(count, total):
        return round((count / total * 100) if total > 0 else 0)
    
    context = {
        'project': project,
        'launches': launches,
        'total_cases': total_cases,
        'draft_cases': draft_cases,
        'draft_percentage': get_percentage(draft_cases, total_cases),
        'review_cases': review_cases,
        'review_percentage': get_percentage(review_cases, total_cases),
        'actual_cases': actual_cases,
        'actual_percentage': get_percentage(actual_cases, total_cases),
        'correction_cases': correction_cases,
        'correction_percentage': get_percentage(correction_cases, total_cases),
    }
    return render(request, 'norma/proj_dashboard.html', context)

def proj_new(request):
    if request.method == "POST":
        # Поддержка AJAX: если пришли поля title/personel — создаём и возвращаем JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'title' in request.POST:
            title = request.POST.get('title', '').strip()
            personel = request.POST.get('personel', '').strip()
            if not title:
                return JsonResponse({'success': False, 'error': 'Название проекта обязательно'})
            proj = Proj(
                title=title,
                personel=personel,
                author=request.user,
                created_date=timezone.now(),
                last_update_date=timezone.now()
            )
            proj.save()
            dashboard_url = reverse('proj_dashboard', args=[proj.pk])
            return JsonResponse({'success': True, 'proj_id': proj.pk, 'title': proj.title, 'dashboard_url': dashboard_url})

        # fallback: обычная форма
        form = ProjCreationForm(request.POST)
        if form.is_valid():
            proj = form.save(commit=False)
            proj.author = request.user
            proj.published_date = timezone.now()
            proj.save()
            return redirect('proj_dashboard', pk=proj.pk)
    else:
        form = ProjCreationForm()
    return render(request, 'norma/proj_edit.html', {'form': form})

def proj_edit(request, pk):
    proj = get_object_or_404(Proj, pk=pk)
    if request.method == "POST":
        # Если это AJAX запрос — возвращаем JSON (используется модаль)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'title' in request.POST:
            title = request.POST.get('title', '').strip()
            personel = request.POST.get('personel', '').strip()
            if not title:
                return JsonResponse({'success': False, 'error': 'Название проекта обязательно'})
            proj.title = title
            proj.personel = personel
            proj.author = request.user
            proj.last_update_date = timezone.now()
            proj.save()
            return JsonResponse({'success': True, 'title': proj.title, 'last_update_date': proj.last_update_date.strftime('%d.%m.%Y %H:%M')})
        else:
            form = ProjCreationForm(request.POST, instance=proj)
            if form.is_valid():
                proj = form.save(commit=False)
                proj.author = request.user
                proj.published_date = timezone.now()
                proj.save()
                return redirect('proj_dashboard', pk=proj.pk)
    else:
        form = ProjCreationForm(instance=proj)
    return render(request, 'norma/proj_edit.html', {'form': form})

def proj_delete(request, pk):
    proj = get_object_or_404(Proj, pk=pk)
    proj.delete()
    
    # Support AJAX delete
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'redirect': reverse('proj_list')})
    
    return redirect('proj_list')

# --- Кейсы (в корне проекта и в папках) ---
def case_detail(request, proj_pk, case_pk):
    project = get_object_or_404(Proj, pk=proj_pk)
    case = get_object_or_404(Cases, pk=case_pk)
    return render(request, 'norma/case_detail.html', {'case': case, 'project': project})

def case_new(request, proj_pk):
    project = get_object_or_404(Proj, pk=proj_pk)
    if request.method == "POST":
        # Получаем данные из POST запроса
        title = request.POST.get('title', '').strip()
        text = request.POST.get('text', '').strip()
        
        # Проверяем наличие данных
        if not title or not text:
            return JsonResponse({'success': False, 'error': 'Название и описание обязательны'})
        
        # Создаем новый кейс
        case = Cases(
            title=title,
            text=text,
            author=request.user,
            project=project,
            created_date=timezone.now(),
            published_date=timezone.now()
        )
        case.save()
        
        # Возвращаем JSON успеха
        return JsonResponse({'success': True, 'case_id': case.id})
    else:
        form = CaseCreationForm()
    return render(request, 'norma/case_edit.html', {'form': form, 'project': project})

def case_edit(request, proj_pk, case_pk):
    project = get_object_or_404(Proj, pk=proj_pk)
    case = get_object_or_404(Cases, pk=case_pk)
    
    if request.method == "POST":
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Проверяем, является ли это AJAX запросом для изменения статуса
        if 'status' in request.POST:
            # AJAX запрос для изменения статуса
            new_status = request.POST.get('status')
            if new_status and new_status in dict(Cases.STATUS_CHOICES):
                case.status = new_status
                case.save()
                return JsonResponse({'success': True, 'status': new_status, 'status_display': case.get_status_display()})
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        elif is_ajax and ('title' in request.POST or 'text' in request.POST):
            # AJAX запрос для редактирования кейса (из модального окна)
            title = request.POST.get('title', '').strip()
            text = request.POST.get('text', '').strip()
            
            if not title or not text:
                return JsonResponse({'success': False, 'error': 'Название и описание обязательны'})
            
            case.title = title
            case.text = text
            case.author = request.user
            case.published_date = timezone.now()
            case.save()
            return JsonResponse({'success': True})
        else:
            # Обычная форма редактирования (для совместимости)
            form = CaseCreationForm(request.POST, instance=case)
            if form.is_valid():
                case = form.save(commit=False)
                case.author = request.user
                case.published_date = timezone.now()
                case.save()
                return redirect('cases_list', pk=project.pk)
    else:
        form = CaseCreationForm(instance=case)
    return render(request, 'norma/case_edit.html', {'form': form, 'project': project, 'case': case})

def case_delete(request, proj_pk, case_pk):
    project = get_object_or_404(Proj, pk=proj_pk)
    case = get_object_or_404(Cases, pk=case_pk)
    case.delete()
    return redirect('cases_list', pk=project.pk)

# --- Список кейсов проекта (корень) ---
def cases_list(request, pk):
    project = get_object_or_404(Proj, pk=pk)
    cases = Cases.objects.filter(project=project).order_by('title')

    if request.method == 'POST':
        form = LaunchCreationForm(request.POST)
        if form.is_valid():
            # Создаем запуск
            launch = form.save(commit=False)
            launch.project = project
            launch.author = request.user
            launch.save()
            
            # Добавляем выбранные кейсы
            case_ids_str = form.cleaned_data.get('case_ids', '')
            if case_ids_str:
                case_ids = [int(cid) for cid in case_ids_str.split(',') if cid.strip()]
                for case_id in case_ids:
                    try:
                        case = Cases.objects.get(id=case_id)
                        TestRunResult.objects.create(
                            launch=launch,
                            case=case,
                            executed_by=request.user,
                            status='in_progress'
                        )
                    except Cases.DoesNotExist:
                        pass
            
            messages.success(request, f'Запуск "{launch.title}" создан!')
            return redirect('launch_detail', launch_id=launch.id)
    else:
        form = LaunchCreationForm()
    
    context = {
        'project': project,
        'cases': cases,
        'form': form,
    }
    return render(request, 'norma/cases_list.html', context)

def launches_list(request, proj_pk):
    """Список всех запусков проекта"""
    project = get_object_or_404(Proj, pk=proj_pk)
    launches = Launches.objects.filter(project=project).order_by('-created_date').prefetch_related('test_results')
    
    # Добавляем статистику к каждому запуску
    for launch in launches:
        launch.total_count = launch.test_results.count()
        launch.passed_count = launch.test_results.filter(status='passed').count()
        launch.failed_count = launch.test_results.filter(status='failed').count()
        launch.in_progress_count = launch.test_results.filter(status='in_progress').count()
        launch.other_count = launch.total_count - launch.passed_count - launch.failed_count - launch.in_progress_count
    
    context = {
        'project': project,
        'launches': launches,
    }
    return render(request, 'norma/launches_list.html', context)

@require_POST
def launch_delete(request, launch_id):
    """Удаление запуска"""
    launch = get_object_or_404(Launches, id=launch_id)
    project = launch.project
    
    # Проверяем доступ: автор проекта или автор запуска или staff
    if not (request.user == project.author or request.user == launch.author or request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Нет доступа для удаления этого запуска')
        return redirect('launches_list', proj_pk=project.pk)
    
    launch.delete()
    messages.success(request, 'Запуск успешно удален')
    return redirect('launches_list', proj_pk=project.pk)

def launch_detail(request, launch_id):
    """Детальная страница запуска"""
    launch = get_object_or_404(Launches, id=launch_id)
    test_results = TestRunResult.objects.filter(launch=launch).select_related('case', 'case__author')

    # Подсчёт статусов для отображения в шапке
    total_cases = test_results.count()
    passed_count = test_results.filter(status='passed').count()
    failed_count = test_results.filter(status='failed').count()
    in_progress_count = test_results.filter(status='in_progress').count()
    unknown_count = test_results.filter(status='unknown').count()
    skipped_count = test_results.filter(status='skipped').count()
    correction_needed_count = test_results.filter(status='correction_needed').count()

    context = {
        'launch': launch,
        'test_results': test_results,
        'total_cases': total_cases,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'in_progress_count': in_progress_count,
        'unknown_count': unknown_count,
        'skipped_count': skipped_count,
        'correction_needed_count': correction_needed_count,
    }
    return render(request, 'norma/launch_detail.html', context)

@require_POST
def update_test_result(request, result_id):
    """Обновление результата тест-кейса (AJAX)"""
    test_result = get_object_or_404(TestRunResult, id=result_id)
    
    # Проверяем, что пользователь имеет доступ к этому запуску.
    # Разрешаем обновление, если пользователь — автор проекта, автор самого кейса или staff/superuser.
    project = test_result.launch.project
    case_author = test_result.case.author if hasattr(test_result, 'case') and test_result.case else None
    if not (request.user == project.author or request.user == case_author or request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Нет доступа'})
    
    form = TestResultUpdateForm(request.POST, instance=test_result)
    if form.is_valid():
        result = form.save(commit=False)
        if result.status != 'in_progress' and not result.executed_by:
            result.executed_by = request.user
            result.executed_at = timezone.now()
        result.save()
        
        return JsonResponse({
            'success': True,
            'status_display': result.get_status_display(),
            'status': result.status,
            'comment': result.comment,
            'executed_by': result.executed_by.username if result.executed_by else '',
            'executed_at': result.executed_at.strftime('%d.%m.%Y %H:%M') if result.executed_at else ''
        })
    else:
        return JsonResponse({'success': False, 'errors': form.errors})