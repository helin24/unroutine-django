# Generated by Django 3.0.3 on 2020-07-02 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sequences', '0008_auto_20200617_0229'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sequence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transitionsJson', models.TextField()),
                ('transitionsCount', models.IntegerField()),
                ('ratingsCount', models.IntegerField(default=0)),
                ('ratingsAverage', models.DecimalField(decimal_places=6, max_digits=7, null=True)),
                ('level', models.CharField(blank=True, choices=[('AB', 'Adult Bronze'), ('AS', 'Adult Silver'), ('AG', 'Adult Gold')], max_length=5, null=True)),
                ('isStep', models.BooleanField(default=False)),
                ('hasJumps', models.BooleanField()),
                ('hasSpins', models.BooleanField()),
                ('initialLeftForC', models.BooleanField(null=True)),
            ],
        ),
    ]