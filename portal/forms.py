from django import forms
from django.contrib.auth.forms import UserCreationForm
from models import *

class SignupForm(UserCreationForm):
    username = forms.EmailField(label='.edu Email')
    is_professor = forms.BooleanField(label='I am a professor',
        widget=forms.CheckboxInput(
            attrs={'style': 'opacity:1;left:0;position:inherit'}))

    def clean_username(self):
        if (self.cleaned_data['username'] is None):
                raise forms.ValidationError(
                    'Email is required.')
        email = self.cleaned_data['username']
        email_handle = email.split('@')[1]
        if School.objects.filter(email_handle=email_handle).first():
            return self.cleaned_data['username']
        else:
            raise forms.ValidationError(
                'Your school is currently not on Virtualecture.')


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=150, widget=forms.PasswordInput)

class CourseForm(forms.ModelForm):
    tas = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={'style': 'opacity:1;left:0;position:inherit'}),
        label='Teaching Assistants',
        queryset=None)
    class Meta:
        model = Course
        exclude = ('school', 'professor')
    def clean_tas(self):
        return self.cleaned_data['tas']