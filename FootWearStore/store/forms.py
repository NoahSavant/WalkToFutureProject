from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from matplotlib import widgets

class RegisterForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
    )
    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','password1','password2']
        widgets={
            'first_name': forms.TextInput(attrs={'class': 'form-control' }),
            'last_name':  forms.TextInput(attrs={'class': 'form-control' }),
            'email': forms.EmailInput(attrs={'class': 'form-control' }),
            'username':forms.TextInput(attrs={'class': 'form-control' }),
        }