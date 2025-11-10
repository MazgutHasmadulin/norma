from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Proj, Folders, Cases, Launches, TestRunResult
from .forms import ProjCreationForm
from django.db.models import Prefetch

def proj_list(request):
    projs = Proj.objects.filter(last_update_date__lte=timezone.now()).order_by('last_update_date')
    return render(request, 'norma/proj_list.html', {'projs':projs})

def proj_dashboard(request, pk):
    proj=Proj.objects.get(pk=pk)
    return render(request, 'norma/proj_dashboard.html', {'proj': proj})

def proj_new(request):
    if request.method == "POST":
        form=ProjCreationForm(request.POST)
        if form.is_valid():
            proj = form.save(commit=False)
            proj.author = request.user
            proj.published_date = timezone.now()
            proj.save()
            return redirect('proj_dashboard', pk=proj.pk)
    else:
        form = ProjCreationForm()
    return render(request, 'norma/proj_edit.html',{'form':form})

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
    proj=get_object_or_404(Proj, pk=pk)
    proj.delete()
    return redirect('norma/base.html')

def cases_list(request, pk):
    # Получаем проект по ID
    project = get_object_or_404(Proj, id=pk)
    
    # Получаем все папки проекта с предзагрузкой связанных тест-кейсов
    folders = Folders.objects.filter(project=project).prefetch_related(
        Prefetch(
            'cases_folder',
            queryset=Cases.objects.all().order_by('title')
        )
    ).order_by('name')
    
    # Получаем тест-кейсы, которые не находятся в папках (если такие есть)
    cases_without_folder = Cases.objects.filter(
        folder__project=project, 
        folder__isnull=True
    ).order_by('title')
    
    context = {
        'project': project,
        'folders': folders,
        'cases_without_folder': cases_without_folder,
    }
    
    return render(request, 'norma/cases_list.html', context)

def case_detail(request, pk):
    """Детальная страница тест-кейса"""
    case = get_object_or_404(Cases, pk=pk)
    return render(request, 'norma/case_detail.html', {'case': case})