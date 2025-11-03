from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Proj

def proj_list(request):
    projs = Proj.objects.filter(last_update_date__lte=timezone.now()).order_by('last_update_date')
    return render(request, 'norma/proj_list.html', {'projs':projs})

def proj_dashboard(request, pk):
    proj=Proj.objects.get(pk=pk)
    return render(request, 'norma/proj_dashboard.html', {'proj': proj})