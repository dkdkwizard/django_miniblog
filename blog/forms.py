from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from ckeditor.fields import RichTextFormField

from blog.models import Blog, Article, Comment


class SignUpForm(UserCreationForm):
    pen_name = forms.CharField(max_length=20, help_text='Required. Your pen name.')
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'style': 'resize:None;'
    }), help_text='About you.')

    class Meta:
        model = User
        fields = ['username', 'pen_name', 'bio', 'password1', 'password2', ]


class EditUserForm(forms.Form):
    pen_name = forms.CharField(max_length=20, help_text='Required. Your pen name.')
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'style': 'resize:None;'
    }), help_text='About you.')

    class Meta:
        model = User
        fields = ['pen_name', 'bio']


class CreateBlogForm(forms.ModelForm):

    def clean_name_field(self):
        nf = self.cleaned_data['name_field']
        # check if name field used
        n = Blog.objects.filter(name_field=nf).count()
        if n > 0:
            raise ValidationError(_('Name Field Used'))
        return nf

    class Meta:
        model = Blog
        fields = ['title', 'name_field', 'description']


class CreateArticleForm(forms.ModelForm):
    content = RichTextFormField()

    class Meta:
        model = Article
        fields = ['title', 'content']


class CommentForm(forms.ModelForm):
    sign = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Your Nickname',
        'style': ' width: 60%;'
    }))
    content = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Leave your comment here',
        'style': ' width: 60%; resize:None;',
    }))

    class Meta:
        model = Comment
        fields = ['sign', 'content']
