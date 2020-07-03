from django.core.management.base import BaseCommand, CommandError
from sequences.models import Move, Edge, Transition, Sequence
from sequences.constants import CATEGORY_CHOICES, CSV_TO_LEVEL_MAP
import csv
import os
from django.conf import settings
from sequences.utils import sequenceNameFromRoutineFeatures
import json

routineDirectory = settings.BASE_DIR + '/routines'

class Command(BaseCommand):
    help = 'Imports elements from CSV documents of routines'
    
    # TODO: Add only a single file

    def handle(self, *args, **options):
        # look at all csv files
        for entry in os.scandir(routineDirectory):
            print(entry.name)
            level, number, direction, sequenceType, letter = entry.name.split('.')[0].split('_')

            with open(entry.path, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                next(reader)

                transitions = [];
                hasJumps = False
                hasSpins = False
                firstFoot = None

                # Considered whether to add hasDirection tracking, but decided to assume all are directional
                # hasDirection = False

                for entryName, moveName, exitName in reader:
                    maybeMove = Move.objects.filter(name__iexact=moveName).first()
                    if maybeMove is not None:
                        move = maybeMove
                    else:
                        # Save new move
                        move = self.saveNewMove(moveName, entryName, exitName)

                    if move is None:
                        print('Unable to import %s' % entry.name)
                        continue

                    if move.category == 'J':
                        hasJumps = True
                    elif move.category == 'S':
                        hasSpins = True

                    # if move.initialLeftForC is not None:
                    #     hasDirection = True

                    if firstFoot is None:
                        firstFoot = entryName[0]
                    entryEdge = Edge.objects.filter(abbreviation=entryName[1:]).first()
                    exitEdge = Edge.objects.filter(abbreviation=exitName[1:]).first()
                    maybeTransition = Transition.objects.filter(entry=entryEdge.id).filter(exit=exitEdge.id).filter(move=move.id).first()
                    if maybeTransition is not None:
                        transition = maybeTransition
                    else:
                        # Save new transition
                        transition = Transition(move=move, entry=entryEdge, exit=exitEdge)
                        try:
                            transition.save()
                            print('Saved: %s -> %s -> %s' % (transition.entry.abbreviation, transition.move.name, transition.exit.abbreviation))
                        except:
                            print('Unable to save: %s -> %s -> %s' % (transition.entry.abbreviation, transition.move.name, transition.exit.abbreviation))

                    if transition is None:
                        print('Unable to import %s' % entry.name)
                        continue

                    transitions.append(self.transitionMap(transition))

            name = sequenceNameFromRoutineFeatures(level, number, letter)
            sequence = Sequence.objects.filter(name=name).first()
            print(CSV_TO_LEVEL_MAP[level])
            if sequence is None:
                sequence = Sequence(
                    name=name,
                    transitionsCount=len(transitions),
                    level=CSV_TO_LEVEL_MAP[level],
                    isStep=sequenceType == 'step',
                    hasJumps=hasJumps,
                    hasSpins=hasSpins,
                    initialLeftForC=(firstFoot == 'L') == (direction == 'c')
                    # initialLeftForC=(firstFoot == 'L') == (direction == 'c') if hasDirection else None
                )
            sequence.transitionsJson = json.dumps({'transitions': transitions})
            sequence.save()

    def transitionMap(self, transition):
        return {
            'move': transition.move.abbreviation,
            'entry': transition.entry.abbreviation,
            'exit': transition.exit.abbreviation,
        }

    def saveNewMove(self, moveName, entryName, exitName):
        print('Not Found: ' + moveName)
        description = input('Description?\n')
        abbreviation = input('Abbreviation?\n')

        categoryLetter = input('Move, spin, or jump? (m, s, j)\n')

        try:
            category = next(filter(lambda choice: choice[0] == categoryLetter.capitalize(), CATEGORY_CHOICES))
        except:
            return None
        if category is None:
            return None
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
            return None

        changeFoot = entryName[0] != exitName[0]

        move = Move(name=moveName, description=description, abbreviation=abbreviation, category=category, initialLeftForC=initialLeftForC, changeFoot=changeFoot)
        try:
            move.save()
            print('Saved: ' + move.name)
            return move
        except:
            print('Unable to save: ' + moveName)
            
        return None

