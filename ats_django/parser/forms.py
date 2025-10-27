from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'country', 'province', 'city', 'min_salary', 'max_salary', 'closing_date', 'description', 'job_type']
        widgets = {
            'closing_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 10}),
        }