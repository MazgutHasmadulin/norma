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




class LaunchCreationForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(required=False, widget=forms.Textarea)
    case_ids = forms.MultipleChoiceField(required=False, widget=forms.MultipleHiddenInput)


class TestResultUpdateForm(forms.ModelForm):
    class Meta:
        model = TestRunResult
        fields = ['status', 'comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Комментарий к результату...'}),
        }
