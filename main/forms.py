from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "text"]


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ["doctor", "user", "date", "time"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "user",
            "is_doctor",
            "img",
            "tel",
            "desc",
            "spec",
            "pesel",
            "city",
            "zip_code",
            "street",
            "addr_number",
        ]
