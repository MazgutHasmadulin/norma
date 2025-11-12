from django.urls import path
from . import views

urlpatterns = [
    # Проекты
    path('', views.proj_list, name='proj_list'),
    path('proj/new/', views.proj_new, name='proj_new'),
    path('proj/<int:pk>/', views.proj_dashboard, name='proj_dashboard'),
    path('proj/<int:pk>/edit/', views.proj_edit, name='proj_edit'),
    path('proj/<int:pk>/delete/', views.proj_delete, name='proj_delete'),

    # Кейсы (в корне проекта или в папке любого уровня)
    path('proj/<int:proj_pk>/case/new/', views.case_new, name='case_new'),
    path('proj/<int:proj_pk>/case/<int:case_pk>/', views.case_detail, name='case_detail'),
    path('proj/<int:proj_pk>/case/<int:case_pk>/edit/', views.case_edit, name='case_edit'),
    path('proj/<int:proj_pk>/case/<int:case_pk>/delete/', views.case_delete, name='case_delete'),

    # Список кейсов проекта (корень)
    path('proj/<int:pk>/cases/', views.cases_list, name='cases_list'),
]