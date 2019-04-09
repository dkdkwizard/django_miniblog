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

    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title

    def get_url(self):
        return reverse('blog', args=[str(self.title)])


class Article(models.Model):
    
    title = models.CharField(max_length=50, help_text='Article\'s title')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    content = RichTextField()
    creation_time = models.DateTimeField('Creation DateTime')
    last_modify_time = models.DateTimeField('Last Modify DateTime')
    
    class Meta:
        ordering = ['creation_time']
    
    def get_url(self):
        return reverse('article', args=[self.blog.title, self.title])


class Comment(models.Model):

    content = models.TextField(max_length=300)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sign = models.CharField(max_length=20)
    time = models.DateTimeField()

    class Meta:
        ordering = ['time']


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pen_name = models.CharField(max_length=20)
    bio = models.TextField('Biography', default='')

    def __str__(self):
        return self.user.username


# update profile with users
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
