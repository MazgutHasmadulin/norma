from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Project, Folder, TestCase
from .serializers import ProjectSerializer, FolderSerializer, TestCaseSerializer
from .forms import ProjectForm
from .forms import FolderForm, TestCaseForm
from django.shortcuts import resolve_url

# =============================================================================
# WEB VIEWS (HTML интерфейс)
# =============================================================================

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'norma/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10
    
    def get_queryset(self):
        return Project.objects.annotate(
            folders_count=Count('folders', distinct=True),
            test_cases_count=Count('test_cases', distinct=True)
        ).order_by('-created_at')

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'norma/project_form.html'
    success_url = reverse_lazy('norma:project-list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Проект успешно создан!')
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'norma/project_form.html'
    success_url = reverse_lazy('norma:project-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Проект успешно обновлен!')
        return super().form_valid(form)

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'norma/project_confirm_delete.html'
    success_url = reverse_lazy('norma:project-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Проект успешно удален!')
        return super().delete(request, *args, **kwargs)

class ProjectDetailWebView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'norma/project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Получаем корневые папки проекта
        root_folders = project.folders.filter(parent_folder__isnull=True)
        
        # Получаем тест-кейсы без папки (в корне проекта)
        root_test_cases = project.test_cases.filter(folder__isnull=True)
        
        context['root_folders'] = root_folders
        context['root_test_cases'] = root_test_cases
        context['folders_count'] = project.folders.count()
        context['test_cases_count'] = project.test_cases.count()
        
        return context


# ----------------
# Web: папки
# ----------------
class FolderCreateWebView(LoginRequiredMixin, CreateView):
    model = Folder
    form_class = FolderForm
    template_name = 'norma/folder_form.html'

    def dispatch(self, request, *args, **kwargs):
        # project_pk is passed via URL
        self.project_pk = kwargs.get('project_pk') or kwargs.get('pk') or kwargs.get('project_id')
        self.parent_folder_pk = kwargs.get('folder_pk') or request.GET.get('parent')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if self.parent_folder_pk:
            initial['parent_folder'] = self.parent_folder_pk
        return initial

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.project_pk)
        parent = None
        if self.parent_folder_pk:
            parent = get_object_or_404(Folder, pk=self.parent_folder_pk)
        form.instance.author = self.request.user
        form.instance.project = project
        form.instance.parent_folder = parent
        messages.success(self.request, 'Папка успешно создана')
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.parent_folder:
            return resolve_url('norma:folder-detail-web', project_pk=self.object.project.pk, pk=self.object.parent_folder.pk)
        return resolve_url('norma:project-detail-web', pk=self.object.project.pk)


class FolderDetailWebView(LoginRequiredMixin, DetailView):
    model = Folder
    template_name = 'norma/folder_detail.html'
    context_object_name = 'folder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder = self.get_object()
        context['subfolders'] = folder.subfolders.all()
        context['test_cases'] = folder.test_cases.all()
        return context


class FolderUpdateView(LoginRequiredMixin, UpdateView):
    model = Folder
    form_class = FolderForm
    template_name = 'norma/folder_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Папка обновлена')
        return super().form_valid(form)

    def get_success_url(self):
        folder = self.object
        if folder.parent_folder:
            return resolve_url('norma:folder-detail-web', project_pk=folder.project.pk, pk=folder.parent_folder.pk)
        return resolve_url('norma:project-detail-web', pk=folder.project.pk)


class FolderDeleteView(LoginRequiredMixin, DeleteView):
    model = Folder
    template_name = 'norma/folder_confirm_delete.html'

    def get_success_url(self):
        folder = self.object
        if folder.parent_folder:
            return resolve_url('norma:folder-detail-web', project_pk=folder.project.pk, pk=folder.parent_folder.pk)
        return resolve_url('norma:project-detail-web', pk=folder.project.pk)

# =============================================================================
# API VIEWS (REST интерфейс)
# =============================================================================

class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def get_queryset(self):
        return Project.objects.annotate(
            folders_count=Count('folders'),
            test_cases_count=Count('test_cases')
        ).order_by('-created_at')

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class FolderListCreateView(generics.ListCreateAPIView):
    serializer_class = FolderSerializer

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        if project_id:
            return Folder.objects.filter(project_id=project_id, parent_folder__isnull=True)
        return Folder.objects.all()

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_id')
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            serializer.save(project=project, author=self.request.user)
        else:
            serializer.save(author=self.request.user)

class NestedFolderListCreateView(generics.ListCreateAPIView):
    serializer_class = FolderSerializer

    def get_queryset(self):
        parent_folder_id = self.kwargs.get('folder_id')
        return Folder.objects.filter(parent_folder_id=parent_folder_id)

    def perform_create(self, serializer):
        parent_folder_id = self.kwargs.get('folder_id')
        parent_folder = get_object_or_404(Folder, id=parent_folder_id)
        serializer.save(
            project=parent_folder.project,
            parent_folder=parent_folder,
            author=self.request.user
        )

class FolderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer

class TestCaseListCreateView(generics.ListCreateAPIView):
    serializer_class = TestCaseSerializer

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        folder_id = self.kwargs.get('folder_id')
        
        if folder_id:
            return TestCase.objects.filter(folder_id=folder_id)
        elif project_id:
            return TestCase.objects.filter(project_id=project_id)
        else:
            return TestCase.objects.all()

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_id')
        folder_id = self.kwargs.get('folder_id')
        
        project = None
        folder = None
        
        if project_id:
            project = get_object_or_404(Project, id=project_id)
        
        if folder_id:
            folder = get_object_or_404(Folder, id=folder_id)
            project = folder.project
        
        if not project and not folder:
            return Response(
                {"error": "Project must be specified"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(
            project=project,
            folder=folder,
            author=self.request.user
        )

class TestCaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer
