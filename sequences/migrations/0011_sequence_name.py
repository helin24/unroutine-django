# Generated by Django 3.0.3 on 2020-07-03 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sequences', '0010_auto_20200702_2324'),
    ]

    operations = [
        migrations.AddField(
            model_name='sequence',
            name='name',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
