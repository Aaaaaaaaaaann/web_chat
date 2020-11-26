from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist

from .models import CustomUser


class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = CustomUser.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError('A user with such a name isn\'t registered.')
        else:
            if not user.is_active:
                raise forms.ValidationError('You have been banned, sorry.')
            else:
                return username


class RegisterForm(forms.ModelForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            CustomUser.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        else:
            raise forms.ValidationError('This username is already used.')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            CustomUser.objects.get(email=email)
        except ObjectDoesNotExist:
            return email
        else:
            raise forms.ValidationError('This email is already used.')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        password_validation.validate_password(cd['password2'])
        return cd['password2']

    def save(self):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password2'])
        user.save()
        return user


class UsernameSearchForm(forms.Form):
    username = forms.CharField(label='Search for a user')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user_to_talk_to = CustomUser.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError('No such a user.')
        else:
            if not user_to_talk_to.is_active:
                raise forms.ValidationError('This user is banned.')
            else:
                return username
