from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from ckeditor.fields import RichTextFormField
from ckeditor_uploader.fields import RichTextUploadingFormField

from blog.models import Blog, Article, Comment


class SignUpForm(UserCreationForm):
    photo = forms.ImageField(label='大頭貼照', required=False)
    pen_name = forms.CharField(label='暱稱', max_length=20, help_text='必填.')
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'style': 'resize:None;'
    }), help_text='關於你.', label='自我介紹')
    password1 = forms.CharField(label=_("密碼"),
                                widget=forms.PasswordInput,
                                help_text='密碼需超過8個字，並至少有一個英文字母')
    password2 = forms.CharField(label=_("再次輸入密碼"),
                                widget=forms.PasswordInput,
                                help_text=_("再次輸入密碼以供驗證"))

    class Meta:
        model = User
        fields = ['username', 'photo', 'pen_name', 'bio', 'password1', 'password2', ]
        labels = {
            'username': '使用者名稱',
        }


class EditUserForm(forms.Form):
    photo = forms.ImageField(label='大頭貼照', required=False)
    pen_name = forms.CharField(label='暱稱', max_length=20, help_text='必填.')
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'style': 'resize:None;'
    }), help_text='關於你.', label='自我介紹')

    class Meta:
        model = User
        fields = ['pen_name', 'bio', 'photo']


class CreateBlogForm(forms.ModelForm):

    def clean_name_field(self):
        nf = self.cleaned_data['name_field']
        # check if name field used
        n = Blog.objects.filter(name_field=nf).count()
        if n > 0:
            raise ValidationError(_('此網域已有人使用'))
        return nf

    class Meta:
        model = Blog
        fields = ['title', 'name_field', 'description']
        labels = {
            'title': '部落格標題',
            'name_field': '部落格網域名',
            'description': '部落格簡介',
        }


class CreateArticleForm(forms.ModelForm):
    content = RichTextUploadingFormField(label='內文')
    cat = forms.ChoiceField(choices=[('unclassified', '--')], widget=forms.Select(attrs={
        'style': 'height:30px;width:20%',
    }))

    def __init__(self, *args, **kwargs):
        cat = kwargs.pop('cat', [])
        super(CreateArticleForm, self).__init__(*args, **kwargs)
        self.fields['cat'].label = '分類'
        self.fields['cat'].choices += [(c, c) for c in cat]

    class Meta:
        model = Article
        fields = ['title', 'cat', 'content']
        labels = {
            'title': '文章標題',
            'content': '內文',
        }
        widgets = {
            'title': forms.TextInput(attrs={'style': 'width:30%;'})
        }


class CategoryForm(forms.Form):
    name = forms.CharField(max_length=20, required=False)

    def clean_name(self):
        n = self.cleaned_data['name']
        if n == 'unclassified':
            raise ValidationError(_('不可使用之分類名'))
        if not n:
            raise ValidationError(_('不可為空白'))
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
        'placeholder': '署名',
        'style': ' width: 60%;'
    }))
    content = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': '你的留言',
        'style': ' width: 60%; resize:None;',
    }))

    class Meta:
        model = Comment
        fields = ['sign', 'content']
