# Generated by Django 3.0.3 on 2020-07-06 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sequences', '0013_remove_transition_rotationdirection'),
    ]

    operations = [
        migrations.AddField(
            model_name='move',
            name='frequency',
            field=models.IntegerField(default=0),
        ),
    ]