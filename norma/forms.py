from django import forms
from .models import Proj, Cases, Launches, TestRunResult

class ProjCreationForm(forms.ModelForm):

    class Meta:
        model = Proj
        fields = ('title',)

class CaseCreationForm(forms.ModelForm):
    class Meta:
        model=Cases
        fields = ('author', 'title', 'text', 'project')




class LaunchCreationForm(forms.ModelForm):
    case_ids = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    class Meta:
        model = Launches
        fields = ['title', 'description']  # Убедитесь, что эти поля есть в модели Launches
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Введите название запуска',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Описание запуска (необязательно)'
            }),
        }


class TestResultUpdateForm(forms.ModelForm):
    class Meta:
        model = TestRunResult
        fields = ['status', 'comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Комментарий к результату...'}),
        }
