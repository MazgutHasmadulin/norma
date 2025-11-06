from django.urls import path
from . import views
urlpatterns = [
    path('', views.proj_list, name='proj_list'),
    path('proj/<int:pk>/', views.proj_dashboard, name='proj_dashboard'),
    path('proj/new/', views.proj_new, name='proj_new'),
    path('proj/<int:pk>/edit/', views.proj_edit, name='proj_edit'),
    path('proj/<int:pk>/delete/', views.proj_delete, name='proj_delete'),
]