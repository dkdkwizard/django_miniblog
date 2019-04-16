from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('createblog', views.createblog, name='createblog'),
    path('allblogs', views.allblogview, name='allblog'),
    path('myblogs', views.MyBlogsView.as_view(), name='myblog'),
    path('edit-user', views.edituserview, name='edituser'),
    re_path(r'^user/(?P<id>\d+)$', views.userpageview, name='user'),
    re_path(r'^(?P<blog>.+)/create$', views.createarticle, name='createarticle'),
    re_path(r'^(?P<blog>.+)/(?P<id>.+)/m$', views.modify_article, name='modify_article'),
    re_path(r'^(?P<blog>.+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<arti>.+)$', views.articleview, name='article'),
    re_path(r'^(?P<blog>.+)$', views.blogview, name='blog'),
]
