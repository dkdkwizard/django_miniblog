import os
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from ckeditor.fields import RichTextField


# Create your models here.
class Blog(models.Model):

    title = models.CharField(max_length=20, help_text='Blog\'s title')
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField('Creation Date')
    name_field = models.CharField(max_length=20, help_text='Blog\'s name field', default='')  # to avoid same title blogs

    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title

    def get_url(self):
        return reverse('blog', args=[self.name_field])
    
    def create_arti_url(self):
        return reverse('createarticle', args=[self.name_field])


class Article(models.Model):
    
    title = models.CharField(max_length=50, help_text='Article\'s title')
    url_name = models.CharField(max_length=50, null=True, blank=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    content = RichTextField(null=True, blank=True)
    creation_time = models.DateTimeField('Creation DateTime')
    last_modify_time = models.DateTimeField('Last Modify DateTime')
    
    class Meta:
        ordering = ['creation_time']
    
    def get_url(self):
        return reverse('article', args=[
            self.blog.name_field,
            self.creation_time.year,
            self.creation_time.month,
            self.creation_time.day,
            self.url_name,
        ])
    
    def modify_url(self):
        return reverse('modify_article', args=[self.blog.name_field, self.id])


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(max_length=300)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sign = models.CharField(max_length=20)
    time = models.DateTimeField()

    class Meta:
        ordering = ['time']


def path_and_rename(path):
    def wrapper(instance, filename):
        ext = filename.split('.')[-1]
        # get filename
        if instance.user:
            filename = '{}.{}'.format(instance.user.pk, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(path, filename)
    return wrapper


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pen_name = models.CharField(max_length=20)
    bio = models.TextField('Biography', default='')
    photo = models.ImageField(upload_to=path_and_rename('portrait/'), default='portrait/default.png')

    def __str__(self):
        return self.user.username


# update profile with users
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
