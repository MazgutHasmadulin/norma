from django.shortcuts import render

def proj_list(request):
    return render(request, 'norma/proj_list.html', {})
