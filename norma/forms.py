from django import forms
from .models import Proj

class ProjCreationForm(forms.ModelForm):

    class Meta:
        model = Proj
        fields = ('title',)