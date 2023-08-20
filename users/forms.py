from django import forms
from django.core.exceptions import ValidationError

from .models import Client


class ClientRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        max_length=255, required=True, widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        max_length=255, required=True, widget=forms.PasswordInput)

    class Meta:
        model = Client
        fields = ('username', 'first_name', 'last_name', 'gender', 'business_name',
                  'address', 'email', 'phone_number', 'agreed_to_terms_and_conditions')

    def clean_agreed_to_terms_and_conditions(self):
        data = self.cleaned_data['agreed_to_terms_and_conditions']
        if not data:
            raise ValidationError(
                'You cannot have an account in the system if you do not accept the terms and conditions.')
        return data

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise ValidationError('Passwords did not match.')
        return password
