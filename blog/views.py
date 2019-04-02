from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse

from blog.models import Blog
from blog.forms import SignUpForm


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
            user.profile.pen_name, user.profile.bio = form.cleaned_data.get('pen_name', 'bio')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user.authenticate(username=user.username, password=raw_password)
            login(request, user)

            return HttpResponseRedirect(reverse('index'))

    else:
        form = SignUpForm()
    context = {
        'form': form
    }
    return render(request, 'signup.html', context=context)
