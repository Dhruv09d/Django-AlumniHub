# Generated by Django 3.0.5 on 2020-09-30 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_relationship'),
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='liked',
            field=models.ManyToManyField(blank=True, related_name='likes', to='profiles.Profile'),
        ),
    ]
