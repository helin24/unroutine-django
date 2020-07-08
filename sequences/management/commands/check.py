from django.core.management.base import BaseCommand, CommandError
import csv
import os
from django.conf import settings

routineDirectory = settings.BASE_DIR + '/routines'

class Command(BaseCommand):
    help = 'Find incorrect moves'

    def handle(self, *args, **options):
        print('starting')
        for entry in os.scandir(routineDirectory):
            with open(entry.path, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for entryName, moveName, exitName in reader:
                    if entryName[1:] == 'BO' and exitName[1:] == 'BO' and moveName == 'Step':
                        print(entry.name)
