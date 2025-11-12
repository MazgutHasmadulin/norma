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
            launch = Launches.objects.create(
                project=project,
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                author=request.user
            )
            
            # Создаем результаты для выбранных кейсов
            case_ids = form.cleaned_data.get('case_ids', [])
            if case_ids:
                cases_to_add = Cases.objects.filter(id__in=case_ids)
                for case in cases_to_add:
                    TestRunResult.objects.create(
                        launch=launch,
                        case=case
                    )
                
                messages.success(request, f'Запуск "{launch.name}" создан с {len(cases_to_add)} кейсами')
                return redirect('launch_detail', launch_id=launch.id)
            else:
                messages.warning(request, 'Не выбрано ни одного кейса')
                return redirect('project_cases_list', project_id=project.id)
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
    test_results = TestRunResult.objects.filter(launch=launch).select_related('testCase', 'testCase__author')
    
    context = {
        'launch': launch,
        'test_results': test_results,
    }
    return render(request, 'norma/launch_detail.html', context)

@require_POST
def update_test_result(request, result_id):
    """Обновление результата тест-кейса (AJAX)"""
    test_result = get_object_or_404(TestRunResult, id=result_id)
    
    # Проверяем, что пользователь имеет доступ к этому запуску
    if test_result.launch.project not in Proj.objects.filter(cases__author=request.user):
        return JsonResponse({'success': False, 'error': 'Нет доступа'})
    
    form = TestResultUpdateForm(request.POST, instance=test_result)
    if form.is_valid():
        result = form.save(commit=False)
        if result.status != 'not_run' and not result.executed_by:
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