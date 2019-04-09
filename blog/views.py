from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views import generic

from blog.models import Blog
from blog.forms import SignUpForm, CreateBlogForm

import datetime


# Create your views here.
def index(request):

    num_blogs = Blog.objects.count()

    context = {
        'num_blogs': num_blogs,
    }

    return render(request, 'index.html', context=context)


def signup(request):
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


class MyBlogsView(generic.ListView):
    model = Blog
    template_name = 'mybloglist.html'
    
    def get_queryset(self):
        return Blog.objects.filter(user=self.request.user)
