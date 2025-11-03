from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Proj
from .forms import ProjCreationForm

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