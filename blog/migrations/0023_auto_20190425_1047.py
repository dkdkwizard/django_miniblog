# Generated by Django 2.1.7 on 2019-04-25 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0022_article_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ['-creation_time']},
        ),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=models.CharField(default='unclassified', max_length=50),
        ),
    ]
