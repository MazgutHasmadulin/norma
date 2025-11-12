from django import forms
from .models import Proj, Cases

class ProjCreationForm(forms.ModelForm):

    class Meta:
        model = Proj
        fields = ('title',)

class CaseCreationForm(forms.ModelForm):
    class Meta:
        model=Cases
        fields = ('author', 'title', 'text', 'project')
