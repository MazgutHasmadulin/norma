from django.urls import path
from . import views
urlpatterns = [
    path('', views.proj_list, name='proj_list'),
    path('proj/<int:pk>/', views.proj_dashboard, name='proj_dashboard'),
    path('proj/new/', views.proj_new, name='proj_new'),
]