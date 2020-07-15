from django.db.models import Q
from .models import Sequence

def sequenceNameFromRoutineFeatures(level, routineNumber, inRoutineLetter):
    return '%s_%s_%s' % (level, routineNumber, inRoutineLetter)

def transitionMap(transition):
    return {
        'move': transition.move.abbreviation,
        'entry': transition.entry.abbreviation,
        'exit': transition.exit.abbreviation,
    }

def parentSequences(level, stepSequence):
    """
    level: String denoting level abbreviation
    stepSequence: boolean denoting whether a step sequence is requested

    returns: iterator of sequences fulfilling requirements to be parents for genetic algorithm
    """
    return Sequence.objects.filter(Q(name__isnull=False) | Q(ratingsCount__gte=5, ratingsAverage__gte=3), isStep=stepSequence, level=level).iterator()

