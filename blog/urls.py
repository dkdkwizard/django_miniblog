from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('createblog', views.createblog, name='createblog'),
    path('myblogs', views.MyBlogsView.as_view(), name='myblog'),
]
