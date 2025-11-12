from django.urls import path, include
from . import views

app_name = 'norma'

# Базовые URL patterns для каждой сущности
project_patterns = [
    path('', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail-api'),
    path('<int:project_id>/folders/', include([
        path('', views.FolderListCreateView.as_view(), name='folder-list-create'),
        path('<int:folder_id>/', include([
            path('', views.FolderDetailView.as_view(), name='folder-detail-api'),
            path('folders/', views.NestedFolderListCreateView.as_view(), name='nested-folder-list-create-api'),
            path('test-cases/', views.TestCaseListCreateView.as_view(), name='test-case-list-create-api'),
        ])),
    ])),
    path('<int:project_id>/test-cases/', views.TestCaseListCreateView.as_view(), name='project-test-case-list-create-api'),
]

folder_patterns = [
    path('', views.FolderListCreateView.as_view(), name='folder-list-create'),
    path('<int:pk>/', views.FolderDetailView.as_view(), name='folder-detail-api'),
]

test_case_patterns = [
    path('', views.TestCaseListCreateView.as_view(), name='test-case-list-create'),
    path('<int:pk>/', views.TestCaseDetailView.as_view(), name='test-case-detail-api'),
]

# Рекурсивные URL для вложенных папок любой глубины
def get_nested_folder_urls(prefix):
    """
    Генерирует URL patterns для вложенных папок любой глубины
    """
    # Одноуровневая генерация: рекурсивная генерация удалена, потому что
    # Django уже поддерживает обработку вложенности через модели (parent_folder).
    # Для рекурсивного разрешения путей можно использовать path converters (например, <path:...>),
    # но для простоты и надёжности возвращаем только шаблон уровня "folder/<id>/...".
    return [
        path(f'{prefix}<int:folder_id>/', include([
            path('', views.FolderDetailView.as_view(), name='folder-detail-api'),
            path('folders/', views.NestedFolderListCreateView.as_view(), name='nested-folder-list-create-api'),
            path('test-cases/', views.TestCaseListCreateView.as_view(), name='test-case-list-create-api'),
        ])),
    ]

# Основные URL patterns
urlpatterns = [
    # Главная страница - список проектов
    path('', views.ProjectListView.as_view(), name='project-list'),

    # 
    path('api-auth/', include('rest_framework.urls')),
    
    # Проекты (API)
    path('api/projects/', include(project_patterns)),
    
    # Папки (глобальный доступ)
    path('api/folders/', include(folder_patterns)),
    
    # Тест-кейсы (глобальный доступ)
    path('api/test-cases/', include(test_case_patterns)),
    
    # Вложенные папки любой глубины (начинаются с проекта)
    path('api/projects/<int:project_id>/folders/', include(get_nested_folder_urls(''))),
    
    # Web интерфейс для проектов
    path('projects/', views.ProjectListView.as_view(), name='project-list-web'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project-create'),
    path('projects/<int:pk>/', views.ProjectDetailWebView.as_view(), name='project-detail-web'),
    path('projects/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project-update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),
    # Web: папки внутри проекта
    path('projects/<int:project_pk>/folders/create/', views.FolderCreateWebView.as_view(), name='folder-create-web'),
    path('projects/<int:project_pk>/folders/<int:folder_pk>/create/', views.FolderCreateWebView.as_view(), name='folder-create-in-folder-web'),
    path('projects/<int:project_pk>/folders/<int:pk>/', views.FolderDetailWebView.as_view(), name='folder-detail-web'),
    path('projects/<int:project_pk>/folders/<int:pk>/update/', views.FolderUpdateView.as_view(), name='folder-update-web'),
    path('projects/<int:project_pk>/folders/<int:pk>/delete/', views.FolderDeleteView.as_view(), name='folder-delete-web'),
]
