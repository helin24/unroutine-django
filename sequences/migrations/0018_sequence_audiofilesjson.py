# Generated by Django 3.0.3 on 2020-07-12 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sequences', '0017_populate_level_frequencies'),
    ]

    operations = [
        migrations.AddField(
            model_name='sequence',
            name='audioFilesJson',
            field=models.TextField(default='{"files": []}'),
        ),
    ]
