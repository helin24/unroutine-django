from django.core.management.base import BaseCommand, CommandError
from sequences.models import Move, Edge, Transition
from sequences.constants import CATEGORY_CHOICES
import csv
import os
from django.conf import settings

routineDirectory = settings.BASE_DIR + '/routines'

class Command(BaseCommand):
    help = 'Imports elements from CSV documents of routines'
    
    # TODO: Add only a single file

    def handle(self, *args, **options):
        self.stdout.write('hello from handle')

        # look at all csv files
        for entry in os.scandir(routineDirectory):
            print(entry.name)
            level, number, direction, sequenceType, letter = entry.name.split('.')[0].split('_')

            with open(entry.path, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                next(reader)
                for entryName, moveName, exitName in reader:
                    maybeMove = Move.objects.filter(name__iexact=moveName).first()
                    if maybeMove is not None:
                        move = maybeMove
                    else:
                        # Save new move
                        print('Not Found: ' + moveName)
                        description = input('Description?\n')
                        abbreviation = input('Abbreviation?\n')

                        categoryLetter = input('Move, spin, or jump? (m, s, j)\n')

                        try:
                            category = next(filter(lambda choice: choice[0] == categoryLetter.capitalize(), CATEGORY_CHOICES))
                        except:
                            continue
                        if category is None:
                            continue
                        else:
                            category = category[0]
                       
                        ilfcLetter = input('Initial is left for clockwise? (t, f, or blank for neither)\n')
                        if ilfcLetter == 't':
                            initialLeftForC = True
                        elif ilfcLetter == 'f':
                            initialLeftForC = False
                        elif ilfcLetter == '':
                            initialLeftForC = None
                        else:
                            continue

                        changeFoot = entryName[0] != exitName[0]

                        move = Move(name=moveName, description=description, abbreviation=abbreviation, category=category, initialLeftForC=initialLeftForC, changeFoot=changeFoot)
                        try:
                            move.save()
                            print('Saved: ' + move.name)
                        except:
                            print('Unable to save: ' + moveName)

                    entryEdge = Edge.objects.filter(abbreviation=entryName[1:]).first()
                    exitEdge = Edge.objects.filter(abbreviation=exitName[1:]).first()
                    maybeTransition = Transition.objects.filter(entry=entryEdge.id).filter(exit=exitEdge.id).filter(move=move.id).first()
                    if maybeTransition is None:
                        # Save new edge
                        transition = Transition(move=move, entry=entryEdge, exit=exitEdge)
                        try:
                            transition.save()
                            print('Saved: %s -> %s -> %s' % (transition.entry.abbreviation, transition.move.name, transition.exit.abbreviation))
                        except:
                            print('Unable to save: %s -> %s -> %s' % (transition.entry.abbreviation, transition.move.name, transition.exit.abbreviation))
