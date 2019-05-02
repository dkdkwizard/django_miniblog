from django.contrib import admin

from blog.models import Blog, Article, Comment, Profile, VisitByDate
# Register your models here.


admin.site.register(Blog)
admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(VisitByDate)
