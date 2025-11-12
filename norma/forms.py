from django import forms
from .models import Project

from .models import Folder, TestCase


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'description', 'parent_folder']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent_folder': forms.HiddenInput(),
        }


class TestCaseForm(forms.ModelForm):
    class Meta:
        model = TestCase
        fields = ['title', 'description', 'preconditions', 'steps', 'expected_result', 'status', 'priority', 'folder']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preconditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'expected_result': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'folder': forms.HiddenInput(),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название проекта'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите описание проекта',
                'rows': 4
            }),
        }
        labels = {
            'name': 'Название проекта',
            'description': 'Описание проекта'
        }
