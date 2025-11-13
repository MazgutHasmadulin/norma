from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Proj, Cases, Launches, TestRunResult
from .forms import ProjCreationForm, CaseCreationForm, LaunchCreationForm, TestResultUpdateForm
from django.db.models import Prefetch

# --- Проекты ---
def proj_list(request):
    projs = Proj.objects.filter(last_update_date__lte=timezone.now()).order_by('last_update_date')
    return render(request, 'norma/proj_list.html', {'projs':projs})

def proj_dashboard(request, pk):
    project = get_object_or_404(Proj, pk=pk)
    launches = Launches.objects.filter(project=project).order_by('-created_date')
    cases_count = Cases.objects.filter(project=project).count()
    context = {
        'project': project,
        'launches': launches,
        'cases_count': cases_count,
    }
    return render(request, 'norma/proj_dashboard.html', context)

def proj_new(request):
    if request.method == "POST":
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
    return redirect('proj_list')

# --- Кейсы (в корне проекта и в папках) ---
def case_detail(request, proj_pk, case_pk):
    project = get_object_or_404(Proj, pk=proj_pk)
    case = get_object_or_404(Cases, pk=case_pk)
    return render(request, 'norma/case_detail.html', {'case': case, 'project': project})

def case_new(request, proj_pk):
    project = get_object_or_404(Proj, pk=proj_pk)
    if request.method == "POST":
        form = CaseCreationForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.author = request.user
            case.published_date = timezone.now()
            case.save()
            return redirect('cases_list', pk=project.pk)
    else:
        form = CaseCreationForm()
    return render(request, 'norma/case_edit.html', {'form': form, 'project': project})

def case_edit(request, proj_pk, case_pk):
    project = get_object_or_404(Proj, pk=proj_pk)
    case = get_object_or_404(Cases, pk=case_pk)
    if request.method == "POST":
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