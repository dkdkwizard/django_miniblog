from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Blog(models.Model):

    title = models.CharField(max_length=20, help_text='Blog\'s title')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField('Creation Date')

    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title


class Article(models.Model):
    
    title = models.CharField(max_length=50, help_text='Article\'s title')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    creation_time = models.DateTimeField('Creation DateTime')
    last_modify_time = models.DateTimeField('Last Modify DateTime')
    
    class Meta:
        ordering = ['creation_time']


class Comemnt(models.Model):

    content = models.TextField(max_length=300)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sign = models.CharField(max_length=20)
    time = models.DateTimeField()

    class Meta:
        ordering = ['time']


class profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pen_name = models.CharField(max_length=20)
    bio = models.TextField('Biography', default='')
