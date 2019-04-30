# Generated by Django 2.1.7 on 2019-04-30 07:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('blog', '0024_auto_20190425_1047'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitByDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_visit', models.PositiveIntegerField(default=0)),
                ('date', models.DateField()),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='total_visit',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='blog',
            name='total_visit',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
