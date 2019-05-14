import os
import json
from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


# Create your models here.
class Blog(models.Model):

    title = models.CharField(max_length=20, help_text='Blog\'s title')
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField('Creation Date')
    name_field = models.CharField(max_length=20, help_text='Blog\'s name field', default='')  # to avoid same title blogs
        
    category = models.CharField(max_length=20000, default='[]')  # list of categorys set and load with json
    total_visit = models.PositiveIntegerField(default=0)
    visitbydate = GenericRelation('VisitByDate')

    def get_url(self):
        return reverse('blog', args=[self.name_field])

    class Meta:
        ordering = ['title']
    
    def set_category(self, x):
        self.category = json.dumps(x)
    
    def get_category(self):
        return json.loads(self.category)

    def __str__(self):
        return self.title
    
    def create_arti_url(self):
        return reverse('createarticle', args=[self.name_field])


class Article(models.Model):
    
    title = models.CharField(max_length=50, help_text='文章的標題')
    url_name = models.CharField(max_length=50, null=True, blank=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    content = RichTextUploadingField(null=True, blank=True)
    category = models.CharField(max_length=50, default='unclassified')
    creation_time = models.DateTimeField('Creation DateTime')
    last_modify_time = models.DateTimeField('Last Modify DateTime')
    total_visit = models.PositiveIntegerField(default=0)
    visitbydate = GenericRelation('VisitByDate')
    
    class Meta:
        ordering = ['-creation_time']
    
    def get_url(self):
        return reverse('article', args=[
            self.blog.name_field,
            self.creation_time.year,
            self.creation_time.month,
            self.creation_time.day,
            self.url_name,
        ])
    
    def del_url(self):
        return reverse('del_article', args=[
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
    sign = models.CharField(max_length=20)
    time = models.DateTimeField()

    class Meta:
        ordering = ['time']


class VisitByDate(models.Model):
    num_visit = models.PositiveIntegerField(default=0)
    date = models.DateField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()


@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        pk = instance.user.pk
        if instance.pk:
            filename = '{}.{}'.format(pk, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pen_name = models.CharField(max_length=20)
    bio = models.TextField('Biography', default='')
    photo = models.ImageField(upload_to=PathAndRename('portrait/'), default='portrait/default.png')

    def __str__(self):
        return f'{self.user.username}_Profile'
        
USING_S3 = os.environ.get('USING_S3', False)


# delete photo after profile is deleted
@receiver(models.signals.post_delete, sender=Profile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.photo != 'portrait/default.png':
        if USING_S3:
            instance.photo.delete(save=False)
        else:
            if os.path.isfile(instance.photo.path):
                os.remove(instance.photo.path)


# delete photo before save new photo

@receiver(models.signals.pre_save, sender=Profile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `Profile` object is updated
    with new file.
    """
    if not instance.pk:
        return False
    old_file = Profile.objects.get(pk=instance.pk).photo
    new_file = instance.photo
    if USING_S3:
        if old_file != 'portrait/default.png':
            old_file.delete(save=False)
    else:
        if old_file != new_file and old_file != 'portrait/default.png':
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)


# update profile with users
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
