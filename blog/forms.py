from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from ckeditor.fields import RichTextFormField
from ckeditor_uploader.fields import RichTextUploadingFormField

from blog.models import Blog, Article, Comment


class SignUpForm(UserCreationForm):
    photo = forms.ImageField(required=False)
    pen_name = forms.CharField(max_length=20, help_text='Required. Your pen name.')
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'style': 'resize:None;'
    }), help_text='About you.')

    class Meta:
        model = User
        fields = ['username', 'photo', 'pen_name', 'bio', 'password1', 'password2', ]


class EditUserForm(forms.Form):
    photo = forms.ImageField(required=False)
    pen_name = forms.CharField(max_length=20, help_text='Required. Your pen name.')
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'style': 'resize:None;'
    }), help_text='About you.')

    class Meta:
        model = User
        fields = ['pen_name', 'bio', 'photo']


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
    content = RichTextUploadingFormField()
    cat = forms.ChoiceField(choices=[('unclassified', '--')])

    def __init__(self, *args, **kwargs):
        cat = kwargs.pop('cat', [])
        super(CreateArticleForm, self).__init__(*args, **kwargs)
        self.fields['cat'].label = 'Category'
        self.fields['cat'].choices += [(c, c) for c in cat]

    class Meta:
        model = Article
        fields = ['title', 'cat', 'content']


class CategoryForm(forms.Form):
    name = forms.CharField(max_length=20, required=False)

    def clean_name(self):
        n = self.cleaned_data['name']
        if n == 'unclassified':
            raise ValidationError(_('Invalid name.'))
        if not n:
            raise ValidationError(_('Can not be Empty'))
        return n


class BaseCategoryFormSet(forms.BaseFormSet):
    
    def clean(self):
        if any(self.errors):
            return
        names = {}
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            name = form.cleaned_data.get('name')
            if name in names:
                raise forms.ValidationError('Categories must have different name')
            names[name] = 1

CategoryFormSet = forms.formset_factory(CategoryForm, formset=BaseCategoryFormSet, max_num=0, can_delete=True)


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
