# Generated by Django 3.0.3 on 2020-06-17 01:39

from django.db import migrations

def populateCanonicalSideFields(apps, schema_editor):
    Move = apps.get_model('sequences', 'Move')
    Transition = apps.get_model('sequences', 'Transition')
    for move in Move.objects.all():
        # find transition
        transition = Transition.objects.select_related('entry', 'exit').exclude(rotationDirection='CCW').filter(move=move.id).first()
        if transition is None:
            print('No transitions for move %s' % move.name)
            continue
        move.changeFoot = transition.entry.abbreviation[0] != transition.exit.abbreviation[0]
        move.initialLeftForC = transition.entry.abbreviation[0] == 'L' if transition.rotationDirection is not None else None
        move.save()

def reverse(apps, schema_editor):
    Move = apps.get_model('sequences', 'Move')
    for move in Move.objects.all():
        move.changeFoot = None
        move.initialLeftForC = None
        move.save()

class Migration(migrations.Migration):

    dependencies = [
        ('sequences', '0006_auto_20200616_0427'),
    ]

    operations = [
        migrations.RunPython(populateCanonicalSideFields, reverse),
    ]