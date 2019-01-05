from random import randint

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Student


class StudentCreationForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput())
    password1 = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={'placeholder': 'Повторите введенный пароль'}))
    
    def clean(self):
        cleaned_data = super().clean()

        if any(self.errors):
            raise forms.ValidationError('Проверьте правильность заполнения полей!')

        if User.objects.filter(email=cleaned_data.get('email')).exists():
            raise forms.ValidationError('Адрес электронной почты уже существует!')

        # If password is less than 4 character or password1 != password2
        if len(cleaned_data.get('password1').strip()) < 4:
            raise forms.ValidationError('Пароль не может быть короче 4 символов!')

        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError('Введенные пароли не совпадают!')

    def save(self, commit=True):
        
        # Create user
        user = User.objects.create_user(username='User' + str(randint(1, 2**200)),
                                        password=self.cleaned_data['password1'], 
                                        email=self.cleaned_data['email'])

        # If everything is OK, create student
        if user:
            return Student.objects.create(user=user)
        return None


class LoginForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput())
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}))
