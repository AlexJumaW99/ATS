from django import forms
from .models import Job, Profile
from django.contrib.auth.models import User

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'country', 'province', 'city', 'min_salary', 'max_salary', 'closing_date', 'description', 'job_type']
        widgets = {
            'closing_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 10}),
        }

class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)

    class Meta:
        model = Profile
        fields = ['username', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['username'].initial = self.instance.user.username

    def save(self, commit=True):
        user = self.instance.user
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
        return super(ProfileUpdateForm, self).save(commit=commit)