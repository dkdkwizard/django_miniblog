from django.shortcuts import render

from blog.models import Blog


# Create your views here.
def index(request):

    num_blogs = Blog.objects.count()

    context = {
        'num_blogs': num_blogs,
    }

    return render(request, 'index.html', context=context)
