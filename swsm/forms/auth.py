# -*- coding: utf-8 -*-
from django import forms


class EmailForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email',
            'placeholder': 'メールアドレス',
        }))

    def clean_email(self):
        return self.cleaned_data['email'].lower()
