# Generated by Django 2.1.7 on 2019-04-16 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_profile_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='photo',
            field=models.ImageField(default='portrait/default.png', upload_to='portrait/'),
        ),
    ]
