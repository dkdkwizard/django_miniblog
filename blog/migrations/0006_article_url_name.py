# Generated by Django 2.1.7 on 2019-04-11 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20190411_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='url_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
