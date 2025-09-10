from django import forms
from .models import UserSettings

class SignInForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class SettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ['theme', 'email_notifications', 'profile_visibility']
