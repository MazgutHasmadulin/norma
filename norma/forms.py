from django import forms
from .models import Proj, Cases, Folders

class ProjCreationForm(forms.ModelForm):

    class Meta:
        model = Proj
        fields = ('title',)

class CaseCreationForm(forms.ModelForm):
    class Meta:
        model=Cases
        fields = ('author', 'title', 'text', 'folder')

class FolderCreationForm(forms.ModelForm):
    class Meta:
        model=Folders
        fields = ('name','level', 'project', 'parent_folder')