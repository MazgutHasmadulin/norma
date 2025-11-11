from django.urls import path
from . import views

urlpatterns = [
    # Проекты
    path('', views.proj_list, name='proj_list'),
    path('proj/new/', views.proj_new, name='proj_new'),
    path('proj/<int:pk>/', views.proj_dashboard, name='proj_dashboard'),
    path('proj/<int:pk>/edit/', views.proj_edit, name='proj_edit'),
    path('proj/<int:pk>/delete/', views.proj_delete, name='proj_delete'),

    # Папки (древовидная вложенность)
    path('proj/<int:proj_pk>/folder/new/', views.folder_new, name='folder_new'),
    path('proj/<int:proj_pk>/folder/<int:folder_pk>/', views.folder_detail, name='folder_detail'),
    path('proj/<int:proj_pk>/folder/<int:folder_pk>/edit/', views.folder_edit, name='folder_edit'),
    path('proj/<int:proj_pk>/folder/<int:folder_pk>/delete/', views.folder_delete, name='folder_delete'),

    # Кейсы (в корне проекта или в папке любого уровня)
    path('proj/<int:proj_pk>/case/new/', views.case_new, name='case_new'),
    path('proj/<int:proj_pk>/case/<int:case_pk>/', views.case_detail, name='case_detail'),
    path('proj/<int:proj_pk>/case/<int:case_pk>/edit/', views.case_edit, name='case_edit'),
    path('proj/<int:proj_pk>/case/<int:case_pk>/delete/', views.case_delete, name='case_delete'),

    # Кейсы внутри папки
    path('proj/<int:proj_pk>/folder/<int:folder_pk>/case/new/', views.case_new, name='case_new_in_folder'),
    path('proj/<int:proj_pk>/folder/<int:folder_pk>/case/<int:case_pk>/', views.case_detail, name='case_detail_in_folder'),
    path('proj/<int:proj_pk>/folder/<int:folder_pk>/case/<int:case_pk>/edit/', views.case_edit, name='case_edit_in_folder'),
    path('proj/<int:proj_pk>/folder/<int:folder_pk>/case/<int:case_pk>/delete/', views.case_delete, name='case_delete_in_folder'),

    # Список кейсов проекта (корень)
    path('proj/<int:pk>/cases/', views.cases_list, name='cases_list'),
]