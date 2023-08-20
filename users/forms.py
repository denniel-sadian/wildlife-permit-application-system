from django import forms
from django.core.exceptions import ValidationError

from .models import Client


class ClientRegistrationForm(forms.ModelForm):

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
