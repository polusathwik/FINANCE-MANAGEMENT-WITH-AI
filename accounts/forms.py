from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.template.context_processors import request
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django import forms
from .models import SecurityQuestions

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([
            f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self
        ]))

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})


    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

SECURITY_QUESTIONS = [
    ('question_1', 'What is your pet’s name?'),
    ('question_2', 'What is your mother’s maiden name?'),
    ('question_3', 'What was the name of your first school?'),
    ('question_4', 'What is your favorite color?'),
    # Add more questions as needed
]

class SecurityQuestionsForm(forms.ModelForm):
    question_1 = forms.ChoiceField(choices=SECURITY_QUESTIONS, label="Security Question 1")
    question_2 = forms.ChoiceField(choices=SECURITY_QUESTIONS, label="Security Question 2")
    answer_1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your answer here'}), label="Answer to Question 1")
    answer_2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your answer here'}), label="Answer to Question 2")

    class Meta:
        model = SecurityQuestions
        fields = ['question_1', 'answer_1', 'question_2', 'answer_2']


class ResetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New Password',
            'class': 'form-control'
        })
    )
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm New Password',
            'class': 'form-control'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")
    answer = forms.CharField(max_length=255, label="Answer")
