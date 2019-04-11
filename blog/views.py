from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic

from blog.models import Blog, Article, Comment
from blog.forms import SignUpForm, CreateBlogForm, CreateArticleForm, CommentForm

import datetime


# Create your views here.
def index(request):
    num_blogs = Blog.objects.count()

    context = {
        'num_blogs': num_blogs,
    }
    for key, item in request.session.items():
        print(key, item)
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


def allblogview(request):
    blog = Blog.objects.order_by('title')
    context = {'blog': blog}
    return render(request, 'all_blog_list.html', context=context)


class MyBlogsView(LoginRequiredMixin, generic.ListView):  # view by Django generic listview
    model = Blog
    template_name = 'mybloglist.html'
    paginate_by = 10

    def get_queryset(self):
        return Blog.objects.filter(user=self.request.user)


def blogview(request, blog):
    blog = Blog.objects.get(name_field=blog)
    context = {
        'blog': blog,
    }

    return render(request, 'blog.html', context=context)


def articleview(request, blog, year, month, day, arti):
    blog = Blog.objects.get(name_field=blog)
    arti = blog.article_set.get(url_name=arti)

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
        'form': form,
    }

    return render(request, 'article.html', context=context)


def userpageview(request, id):
    user = User.objects.get(pk=id)
    profile = user.profile
    blog = user.blog_set
    comment = user.comment_set
    context = {
        'that_user': user,
        'blog': blog,
        'comment': comment,
    }

    return render(request, 'user.html', context=context)


@login_required
def createblog(request):
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
def createarticle(request, blog):
    blog = Blog.objects.get(name_field=blog)
    if request.user != blog.user:
        next = request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(next)
    
    if request.method == 'POST':
        form = CreateArticleForm(request.POST)
        if form.is_valid():
            article = Article.objects.create(blog=blog, creation_time=datetime.datetime.now(), last_modify_time=datetime.datetime.now())
            article.title = form.cleaned_data.get('title')
            n = blog.article_set.filter(title=article.title).filter(creation_time__date=article.creation_time.date()).count()
            if n > 0:
                article.url_name = article.title + f'-{n+1}'
            else:
                article.url_name = article.title

            article.content = form.cleaned_data.get('content')
            article.save()
            dt = article.creation_time
            return HttpResponseRedirect(reverse('article', kwargs={
                'blog': blog.name_field,
                'arti': article.url_name,
                'year': dt.year,
                'month': dt.month,
                'day': dt.day,
            }))

    else:
        form = CreateArticleForm()
    context = {
        'form': form
    }
    return render(request, 'createarticle.html', context=context)


@login_required
def modify_article(request, blog, id):
    blog = Blog.objects.get(name_field=blog)
    if request.user != blog.user:
        next = request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(next)
    article = Article.objects.get(pk=id)
    if request.method == 'POST':
        form = CreateArticleForm(request.POST)
        if form.is_valid():
            article.title = form.cleaned_data.get('title')
            article.content = form.cleaned_data.get('content')
            article.save()
            dt = article.creation_time
            return HttpResponseRedirect(reverse('article', kwargs={
                'blog': article.blog.name_field,
                'arti': article.url_name,
                'year': dt.year,
                'month': dt.month,
                'day': dt.day,
            }))

    else:
        form = CreateArticleForm(
            initial={
                'title': article.title,
                'content': article.content,
            }
        )

    context = {
        'form': form
    }
    return render(request, 'modifyarticle.html', context=context)
