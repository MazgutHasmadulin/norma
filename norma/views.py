from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Proj, Cases, Launches, TestRunResult
from .forms import ProjCreationForm, CaseCreationForm
from django.db.models import Prefetch

# --- Проекты ---
def proj_list(request):
    projs = Proj.objects.filter(last_update_date__lte=timezone.now()).order_by('last_update_date')
    return render(request, 'norma/proj_list.html', {'projs':projs})

def proj_dashboard(request, pk):
    proj = get_object_or_404(Proj, pk=pk)
    return render(request, 'norma/proj_dashboard.html', {'proj': proj})

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
    return render(request, 'norma/case_edit.html', {'form': form, 'project': project, 'case': case})

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
    project = get_object_or_404(Proj, id=pk)
    cases = Cases.objects.filter(project=project).order_by('title')
    context = {
        'project': project,
        'cases': cases,
    }
    return render(request, 'norma/cases_list.html', context)