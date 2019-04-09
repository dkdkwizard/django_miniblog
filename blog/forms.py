from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from blog.models import Blog


class SignUpForm(UserCreationForm):
    pen_name = forms.CharField(max_length=20, help_text='Required. Your pen name.')
    bio = forms.CharField(widget=forms.Textarea, help_text='About you.')

    class Meta:
        model = User
        fields = ['username', 'pen_name', 'bio', 'password1', 'password2', ]


class CreateBlogForm(forms.ModelForm):

    class Meta:
        model = Blog
        fields = ['title', 'description']
