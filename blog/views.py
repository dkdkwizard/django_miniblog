from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Min, Sum
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic
from django.conf import settings

from blog.models import Blog, Article, Comment, VisitByDate
from blog.forms import SignUpForm, CreateBlogForm, CreateArticleForm, CommentForm, EditUserForm, CategoryForm, CategoryFormSet
from blog.utils import add_visit_number, n_day_hot

import datetime


# Create your views here.
def index(request):
    new_arti = Article.objects.order_by('-creation_time')[:3]
    hot_blogs = n_day_hot(7, Blog)[:3]
    hot_artis = n_day_hot(7, Article)[:3]
    context = {
        'new_arti': new_arti,
        'hot_blogs': hot_blogs,
        'hot_artis': hot_artis,
    }
    return render(request, 'index.html', context=context)


def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.pen_name, user.profile.bio = form.cleaned_data.get('pen_name'), form.cleaned_data.get('bio')
            if form.cleaned_data['photo']:
                user.profile.photo = form.cleaned_data['photo']
            user.profile.save()
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)

            return HttpResponseRedirect(reverse('index'))

    else:
        form = SignUpForm()
    context = {
        'form': form
    }
    return render(request, 'signup.html', context=context)


def user_page_view(request, id):
    user = get_object_or_404(User, pk=id)
    profile = user.profile
    blog = user.blog_set

    if request.method == 'POST':
        if 'remove' in request.POST:
            profile.photo = 'portrait/default.png'
            profile.save()
            return HttpResponseRedirect(request.path)
    context = {
        'that_user': user,
        'blog': blog,
    }

    return render(request, 'user.html', context=context)


@login_required
def edit_user_view(request):
    user = request.user
    prof = user.profile
    if request.method == 'POST':
        form = EditUserForm(request.POST, request.FILES)
        if form.is_valid():
            prof.pen_name = form.cleaned_data['pen_name']
            prof.bio = form.cleaned_data['bio']
            if form.cleaned_data['photo']:
                prof.photo = form.cleaned_data['photo']
            prof.save()
            return HttpResponseRedirect(reverse('user', args=[user.pk]))
    else:
        form = EditUserForm(
            initial={
                'pen_name': prof.pen_name,
                'bio': prof.bio,
            }
        )
    context = {
        'form': form,
    }
    return render(request, 'edituser.html', context=context)


def all_blog_view(request):
    blog = Blog.objects.order_by('title')
    context = {'blog': blog}
    return render(request, 'all_blog_list.html', context=context)


class MyBlogsView(LoginRequiredMixin, generic.ListView):  # view by Django generic listview
    model = Blog
    template_name = 'mybloglist.html'
    paginate_by = 10

    def get_queryset(self):
        return Blog.objects.filter(user=self.request.user)


def blog_view(request, blog):
    blog = get_object_or_404(Blog, name_field=blog)
    visit_by_date = add_visit_number(request, blog)
    arti = blog.article_set.all()
    cat = blog.get_category()
    cat_num = [0] * len(cat)
    for i in range(len(cat)):
        cat_num[i] = arti.filter(category__exact=cat[i]).count()
    cat = sorted(zip(cat, cat_num))
    num_unclass = arti.filter(category__exact='unclassified').count()
    context = {
        'blog': blog,
        'article': arti,
        'cat': cat,
        'num_unclass': num_unclass,
        'visit_by_date': visit_by_date,
    }

    return render(request, 'blog.html', context=context)


def blog_query_by_category_view(request, blog, cat):
    blog = get_object_or_404(Blog, name_field=blog)
    visit_by_date = add_visit_number(request, blog)
    arti_all = blog.article_set.all()
    arti = blog.article_set.filter(category__exact=cat)
    
    cat = blog.get_category()
    cat_num = [0] * len(cat)
    for i in range(len(cat)):
        cat_num[i] = arti_all.filter(category__exact=cat[i]).count()
    cat = sorted(zip(cat, cat_num))
    num_unclass = arti_all.filter(category__exact='unclassified').count()
    context = {
        'blog': blog,
        'article': arti,
        'cat': cat,
        'num_unclass': num_unclass,
        'visit_by_date': visit_by_date,
    }

    return render(request, 'blog.html', context=context)


@login_required
def edit_category_view(request, blog):
    blog = get_object_or_404(Blog, name_field=blog)
    cat = blog.get_category()
    # CategoryFormSet = forms.formset_factory(CategoryForm, formset=BaseCategoryFormSet, max_num=20)
    if request.user != blog.user:
        next = request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(next)
    
    if request.method == 'POST':
        if 'edit' in request.POST:
            formset = CategoryFormSet(request.POST)
            if len(cat) < 20:
                form2 = CategoryForm()
            if formset.is_valid():
                for idx, form in enumerate(formset.forms):
                    n = form.cleaned_data['name']
                    if n != cat[idx]:
                        arti = blog.article_set.filter(category__exact=cat[idx]).update(category=n)
                        cat[idx] = form.cleaned_data['name']
                        cat = sorted(cat)
                        blog.set_category(cat)
                        blog.save()
                return HttpResponseRedirect(request.path)
        if 'delete' in request.POST:
            formset = CategoryFormSet(request.POST)
            form2 = CategoryForm(request.POST)
            if formset.is_valid():
                for idx, form in enumerate(formset.forms):
                    if form.cleaned_data['DELETE']:
                        arti = blog.article_set.filter(category__exact=cat[idx]).update(category='')
                        del cat[idx]
                        blog.set_category(cat)
                        blog.save()
                return HttpResponseRedirect(request.path)
        if 'add' in request.POST:
            formset = CategoryFormSet(initial=[{'name': i} for i in cat])
            form2 = CategoryForm(request.POST)
            if form2.is_valid():
                n = form2.cleaned_data['name']
                if n in cat:
                    form2.add_error('name', 'This category already exist.')
                else:
                    cat.append(n)
                    cat = sorted(cat)
                    blog.set_category(cat)
                    blog.save()
                    return HttpResponseRedirect(request.path)
    else:
        formset = CategoryFormSet(initial=[{'name': i} for i in cat])
        if len(cat) < 20:
            form2 = CategoryForm()
    context = {
        'blog': blog,
        'cat': cat,
        'formset': formset,
        'form2': form2,
    }

    return render(request, 'editcategory.html', context=context)
    

def article_view(request, blog, year, month, day, arti):
    blog = get_object_or_404(Blog, name_field=blog)
    visit_by_date_blog = add_visit_number(request, blog)
    arti_all = blog.article_set.all()
    arti = get_object_or_404(arti_all.filter(
        creation_time__year=year,
        creation_time__month=month,
        creation_time__day=day),
        url_name=arti
    )
    visit_by_date_arti = add_visit_number(request, arti)
    last_arti_cat = arti_all.filter(category__exact=arti.category, creation_time__lt=arti.creation_time).first()
    next_arti_cat = arti_all.filter(category__exact=arti.category, creation_time__gt=arti.creation_time).last()
    cat = blog.get_category()
    cat_num = [0] * len(cat)
    for i in range(len(cat)):
        cat_num[i] = arti_all.filter(category__exact=cat[i]).count()
    cat = sorted(zip(cat, cat_num))
    num_unclass = arti_all.filter(category__exact='unclassified').count()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment.objects.create(article=arti, time=datetime.datetime.now())
            if request.user.is_authenticated:
                comment.user = request.user
                comment.sign = request.user.profile.pen_name
            else:
                comment.sign = 'guest'
            if form.cleaned_data['sign']:
                comment.sign = form.cleaned_data['sign']
            comment.content = form.cleaned_data['content']
            comment.save()

            return HttpResponseRedirect(request.path)

    else:
        form = CommentForm()

    context = {
        'arti': arti,
        'blog': blog,
        'form': form,
        'cat': cat,
        'num_unclass': num_unclass,
        'last_arti_cat': last_arti_cat,
        'next_arti_cat': next_arti_cat,
        'visit_by_date': visit_by_date_blog,
    }

    return render(request, 'article.html', context=context)


def delete_article_view(request, blog, year, month, day, arti):
    blog = get_object_or_404(Blog, name_field=blog)
    arti = get_object_or_404(blog.article_set.filter(
        creation_time__year=year,
        creation_time__month=month,
        creation_time__day=day),
        url_name=arti
    )
    arti.delete()
    return HttpResponseRedirect(reverse('blog', args=[blog.name_field]))


@login_required
def create_blog_view(request):
    if request.method == 'POST':
        form = CreateBlogForm(request.POST)
        if form.is_valid():
            blog = Blog.objects.create(user=request.user, date=datetime.date.today())
            blog.title, blog.description = form.cleaned_data['title'], form.cleaned_data['description']
            blog.name_field = form.cleaned_data['name_field']
            blog.save()

            return HttpResponseRedirect(reverse('blog', args=[blog.name_field]))

    else:
        form = CreateBlogForm()
    context = {
        'form': form
    }
    return render(request, 'createblog.html', context=context)


@login_required
def create_article_view(request, blog):
    blog = get_object_or_404(Blog, name_field=blog)
    cat = blog.get_category()
    if request.user != blog.user:
        next = request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(next)
    
    if request.method == 'POST':
        form = CreateArticleForm(request.POST, cat=cat)
        if form.is_valid():
            article = Article.objects.create(blog=blog, creation_time=datetime.datetime.now(), last_modify_time=datetime.datetime.now())
            article.title = form.cleaned_data.get('title')
            n = blog.article_set.filter(title=article.title).filter(creation_time__date=article.creation_time.date()).count()
            t = article.title.replace(' ', '-')
            if n > 0:
                article.url_name = t + f'-{n+1}'
            else:
                article.url_name = t
            article.content = form.cleaned_data.get('content')
            article.category = form.cleaned_data.get('cat')
            article.save()
            dt = article.creation_time
            return HttpResponseRedirect(article.get_url())

    else:
        form = CreateArticleForm(cat=cat)
    context = {
        'form': form
    }
    return render(request, 'createarticle.html', context=context)


@login_required
def modify_article_view(request, blog, id):
    blog = get_object_or_404(Blog, name_field=blog)
    cat = blog.get_category()
    if request.user != blog.user:
        next = request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(next)
    article = get_object_or_404(Article, pk=id)
    if request.method == 'POST':
        form = CreateArticleForm(request.POST, cat=cat)
        if form.is_valid():
            article.title = form.cleaned_data.get('title')
            article.content = form.cleaned_data.get('content')
            article.category = form.cleaned_data.get('cat')
            article.save()
            dt = article.creation_time
            return HttpResponseRedirect(article.get_url())

    else:
        form = CreateArticleForm(
            cat=cat,
            initial={
                'title': article.title,
                'content': article.content,
                'cat': article.category,
            }
        )

    context = {
        'arti': article,
        'form': form,
    }
    return render(request, 'modifyarticle.html', context=context)
