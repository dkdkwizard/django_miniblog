from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('createblog', views.create_blog_view, name='createblog'),
    path('allblogs', views.all_blog_view, name='allblog'),
    path('myblogs', views.MyBlogsView.as_view(), name='myblog'),
    path('edit-user', views.edit_user_view, name='edituser'),
    re_path(r'^user/(?P<id>\d+)$', views.user_page_view, name='user'),
    re_path(r'^(?P<blog>.+)/create$', views.create_article_view, name='createarticle'),
    re_path(r'^(?P<blog>.+)/manage$', views.blog_manage_view, name='blog_manage'),
    re_path(r'^(?P<blog>.+)/category/edit$', views.edit_category_view, name='editcategory'),
    re_path(r'^(?P<blog>.+)/category/(?P<cat>.+)$', views.blog_query_by_category_view, name='blog_category_query'),
    re_path(r'^(?P<blog>.+)/(?P<id>.+)/m$', views.modify_article_view, name='modify_article'),
    re_path(r'^(?P<blog>.+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<arti>.+)/del$', views.delete_article_view, name='del_article'),
    re_path(r'^(?P<blog>.+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<arti>.+)$', views.article_view, name='article'),
    re_path(r'^(?P<blog>.+)$', views.blog_view, name='blog'),
]
