from django.core.management.base import BaseCommand, CommandError
import csv
import os
from django.conf import settings
from django.db.models import Sum
from sequences.models import Sequence, Move
from sequences.generator import Generator

class Command(BaseCommand):
    help = 'Look at chi square of sequences'

    def handle(self, *args, **options):
        bronze_step_total = Move.objects.aggregate(Sum('frequency_adult_bronze_step'))['frequency_adult_bronze_step__sum']
        bronze_nonstep_total = Move.objects.aggregate(Sum('frequency_adult_bronze_nonstep'))['frequency_adult_bronze_nonstep__sum']

        bronze_step_map = {}
        bronze_nonstep_map = {}

        for move in Move.objects.all().iterator():
            bronze_step_map[move.abbreviation] = move.frequency_adult_bronze_step * 1.0 / bronze_step_total
            bronze_nonstep_map[move.abbreviation] = move.frequency_adult_bronze_nonstep * 1.0 / bronze_nonstep_total

        print(bronze_step_map)

        for sequence in Sequence.objects.filter(name__startswith='bronze', isStep=True).iterator():
            transitions = Generator().transitionsWithFootFromSequence(sequence, True)

            sequence_map = {}

            for t in transitions:
                if t.move.abbreviation not in sequence_map:
                    sequence_map[t.move.abbreviation] = 0
                sequence_map[t.move.abbreviation] += 1

            sumSquares = 0.0
            for moveAbbr, frequency in bronze_step_map.items():
                if frequency > 0:
                    sumSquares += ((frequency * len(transitions) - sequence_map.get(moveAbbr, 0) * 1.0) ** 2 / (frequency * len(transitions)))

            print('Name: %s, length %d: %d' % (sequence.name, len(transitions), sumSquares))


            # every 5 moves
            # every 10 moves
            # total sequence

