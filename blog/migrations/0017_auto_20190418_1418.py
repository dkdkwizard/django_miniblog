# Generated by Django 2.1.7 on 2019-04-18 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_blog_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='category',
            field=models.CharField(default='[]', max_length=2000),
        ),
    ]
