from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views import generic

from blog.models import Blog, Article
from blog.forms import SignUpForm, CreateBlogForm, CreateArticleForm

import datetime


# Create your views here.
def index(request):
    num_blogs = Blog.objects.count()

    context = {
        'num_blogs': num_blogs,
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


@login_required
def createblog(request):
    if request.method == 'POST':
        form = CreateBlogForm(request.POST)
        if form.is_valid():
            blog = Blog.objects.create(user=request.user, date=datetime.date.today())
            blog.title, blog.description = form.cleaned_data.get('title'), form.cleaned_data.get('description')
            blog.save()

            return HttpResponseRedirect(reverse('index'))

    else:
        form = CreateBlogForm()
    context = {
        'form': form
    }
    return render(request, 'createblog.html', context=context)


@login_required
def createarticle(request, blogid):
    if request.method == 'POST':
        form = CreateArticleForm(request.POST)
        if form.is_valid():
            article = Article.objects.create(creation_time=datetime.datetime.now(), last_modify_time=datetime.datetime.now())
            article.content = form.cleaned_data.get('content')
            article.save()

            return HttpResponseRedirect(reverse('index'))

    else:
        form = CreateArticleForm()
    context = {
        'form': form
    }
    return render(request, 'createarticle.html', context=context)


class MyBlogsView(generic.ListView):  # view by Django generic listview
    model = Blog
    template_name = 'mybloglist.html'
    paginate_by = 10

    def get_queryset(self):
        return Blog.objects.filter(user=self.request.user)


def blogview(request, title):
    blog = Blog.objects.get(title=title)
    context = {
        'blog': blog,
    }

    return render(request, 'blog.html', context=context)
