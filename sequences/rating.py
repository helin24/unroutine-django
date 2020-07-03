from django.db import transaction
from .models import Sequence

@transaction.atomic
def updateRating(sequenceId, rating):
    sequence = Sequence.objects.get(pk=sequenceId)

    if sequence.ratingsCount == 0:
        sequence.ratingsAverage = rating
        sequence.ratingsCount = 1
    else:
        sequence.ratingsAverage = (sequence.ratingsAverage * sequence.ratingsCount + rating) / (sequence.ratingsCount + 1)
        sequence.ratingsCount += 1

    sequence.save()


