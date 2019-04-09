from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('createblog', views.createblog, name='createblog'),
    path('createarticle', views.createarticle, name='createarticle'),
    path('myblogs', views.MyBlogsView.as_view(), name='myblog'),
    re_path(r'^(?P<blog>.+)/(?P<title>.+)$', views.articleview, name='article'),
    re_path(r'^(?P<title>.+)$', views.blogview, name='blog'),
]
