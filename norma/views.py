
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Proj, Folders, Cases, Launches, TestRunResult
from .forms import ProjCreationForm, CaseCreationForm, FolderCreationForm
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

# --- Папки (древовидная структура) ---
def folder_detail(request, proj_pk, folder_pk):
    project = get_object_or_404(Proj, pk=proj_pk)
    folder = get_object_or_404(Folders, pk=folder_pk, project=project)
    subfolders = folder.subfolders.all().order_by('name')
    cases = folder.cases_folder.all().order_by('title')
    return render(request, 'norma/folder_detail.html', {
        'project': project,
        'folder': folder,
        'subfolders': subfolders,
        'cases': cases,
    })

def folder_new(request, proj_pk, folder_pk=None):
    project = get_object_or_404(Proj, pk=proj_pk)
    parent_folder = None
    if folder_pk:
        parent_folder = get_object_or_404(Folders, pk=folder_pk, project=project)
    if request.method == "POST":
        form = FolderCreationForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.project = project
            folder.parent_folder = parent_folder
            folder.save()
            return redirect('folder_detail', proj_pk=project.pk, folder_pk=folder.pk)
    else:
        form = FolderCreationForm(initial={'project': project, 'parent_folder': parent_folder})
    return render(request, 'norma/folder_edit.html', {'form': form, 'project': project, 'parent_folder': parent_folder})

def folder_edit(request, proj_pk, folder_pk):
    project = get_object_or_404(Proj, pk=proj_pk)
    folder = get_object_or_404(Folders, pk=folder_pk, project=project)
    if request.method == "POST":
        form = FolderCreationForm(request.POST, instance=folder)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.project = project
            folder.save()
            return redirect('folder_detail', proj_pk=project.pk, folder_pk=folder.pk)
    else:
        form = FolderCreationForm(instance=folder)
    return render(request, 'norma/folder_edit.html', {'form': form, 'project': project, 'folder': folder})

def folder_delete(request, proj_pk, folder_pk):
    project = get_object_or_404(Proj, pk=proj_pk)
    folder = get_object_or_404(Folders, pk=folder_pk, project=project)
    parent_folder = folder.parent_folder
    folder.delete()
    if parent_folder:
        return redirect('folder_detail', proj_pk=project.pk, folder_pk=parent_folder.pk)
    else:
        return redirect('proj_dashboard', pk=project.pk)

# --- Кейсы (в корне проекта и в папках) ---
def case_detail(request, proj_pk, case_pk, folder_pk=None):
    project = get_object_or_404(Proj, pk=proj_pk)
    case = get_object_or_404(Cases, pk=case_pk, folder__project=project)
    return render(request, 'norma/case_detail.html', {'case': case, 'project': project})

def case_new(request, proj_pk, folder_pk=None):
    project = get_object_or_404(Proj, pk=proj_pk)
    folder = None
    if folder_pk:
        folder = get_object_or_404(Folders, pk=folder_pk, project=project)
    if request.method == "POST":
        form = CaseCreationForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.author = request.user
            case.published_date = timezone.now()
            case.folder = folder
            case.save()
            if folder:
                return redirect('folder_detail', proj_pk=project.pk, folder_pk=folder.pk)
            else:
                return redirect('proj_dashboard', pk=project.pk)
    else:
        form = CaseCreationForm(initial={'author': request.user, 'folder': folder})
    return render(request, 'norma/case_edit.html', {'form': form, 'project': project, 'folder': folder})

def case_edit(request, proj_pk, case_pk, folder_pk=None):
    project = get_object_or_404(Proj, pk=proj_pk)
    case = get_object_or_404(Cases, pk=case_pk, folder__project=project)
    if request.method == "POST":
        form = CaseCreationForm(request.POST, instance=case)
        if form.is_valid():
            case = form.save(commit=False)
            case.author = request.user
            case.published_date = timezone.now()
            case.save()
            folder = case.folder
            if folder:
                return redirect('folder_detail', proj_pk=project.pk, folder_pk=folder.pk)
            else:
                return redirect('proj_dashboard', pk=project.pk)
    else:
        form = CaseCreationForm(instance=case)
    return render(request, 'norma/case_edit.html', {'form': form, 'project': project, 'case': case})

def case_delete(request, proj_pk, case_pk, folder_pk=None):
    project = get_object_or_404(Proj, pk=proj_pk)
    case = get_object_or_404(Cases, pk=case_pk, folder__project=project)
    folder = case.folder
    case.delete()
    if folder:
        return redirect('folder_detail', proj_pk=project.pk, folder_pk=folder.pk)
    else:
        return redirect('proj_dashboard', pk=project.pk)

# --- Список кейсов проекта (корень) ---
def cases_list(request, pk):
    project = get_object_or_404(Proj, id=pk)
    folders = Folders.objects.filter(project=project, parent_folder=None).prefetch_related(
        Prefetch('cases_folder', queryset=Cases.objects.all().order_by('title'))
    ).order_by('name')
    cases_without_folder = Cases.objects.filter(folder__project=project, folder__isnull=True).order_by('title')
    context = {
        'project': project,
        'folders': folders,
        'cases_without_folder': cases_without_folder,
    }
    return render(request, 'norma/cases_list.html', context)