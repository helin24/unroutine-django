# Generated by Django 3.0.3 on 2020-02-16 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sequences', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='move',
            name='rotationDirection',
            field=models.CharField(blank=True, choices=[('CW', 'Clockwise'), ('CCW', 'Counter-Clockwise')], max_length=3, null=True),
        ),
    ]
