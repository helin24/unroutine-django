from django.core.management.base import BaseCommand, CommandError
from sequences.models import Move, Edge, Transition
import csv
import os
from django.conf import settings

routineDirectory = settings.BASE_DIR + '/routines'

class Command(BaseCommand):
    help = 'Imports elements from CSV documents of routines'

    def handle(self, *args, **options):
        self.stdout.write('hello from handle')

        # look at all csv files
        print(routineDirectory)
        for filename in os.scandir(routineDirectory):
            print(filename)


        # look at each move and search for it in move
        # if not, ask for input for description, abbreviation, category, initialLeftForC

        # also check if the transition matches
        # if not, ask for input of whether or not to add
