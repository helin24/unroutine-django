from django.test import TestCase
from sequences.utils import parentSequences
from sequences.models import Sequence
from sequences.constants import LevelAbbreviation, RATINGS_COUNT_REQUIREMENT, RATINGS_AVERAGE_REQUIREMENT

class UtilsTestCase(TestCase):
    def setUp(self):
        self.primarySequence1 = Sequence.objects.create(
            transitionsJson='',
            transitionsCount=0,
            ratingsCount=0,
            ratingsAverage=None,
            level=LevelAbbreviation.ADULT_SILVER.value,
            isStep=True,
            hasJumps=False,
            hasSpins=True,
            initialLeftForC=True,
            name='Silver step sequence',
            audioFilesJson='{"files": []}',
        )
        self.primarySequence2 = Sequence.objects.create(
            transitionsJson='',
            transitionsCount=0,
            ratingsCount=0,
            ratingsAverage=None,
            level=LevelAbbreviation.ADULT_SILVER.value,
            isStep=True,
            hasJumps=False,
            hasSpins=True,
            initialLeftForC=True,
            name='Silver step sequence 2',
            audioFilesJson='{"files": []}',
        )
        self.primarySequenceNotStep = Sequence.objects.create(
            transitionsJson='',
            transitionsCount=0,
            ratingsCount=0,
            ratingsAverage=None,
            level=LevelAbbreviation.ADULT_SILVER.value,
            isStep=False,
            hasJumps=False,
            hasSpins=True,
            initialLeftForC=True,
            name='Silver step sequence 3',
            audioFilesJson='{"files": []}',
        )
        self.primarySequenceBronze = Sequence.objects.create(
            transitionsJson='',
            transitionsCount=0,
            ratingsCount=0,
            ratingsAverage=None,
            level=LevelAbbreviation.ADULT_BRONZE.value,
            isStep=True,
            hasJumps=False,
            hasSpins=True,
            initialLeftForC=True,
            name='Bronze step sequence 1',
            audioFilesJson='{"files": []}',
        )
        self.badSequence = Sequence.objects.create(
            transitionsJson='',
            transitionsCount=0,
            ratingsCount=RATINGS_COUNT_REQUIREMENT + 1,
            ratingsAverage=RATINGS_AVERAGE_REQUIREMENT - 1,
            level=LevelAbbreviation.ADULT_SILVER.value,
            isStep=True,
            hasJumps=False,
            hasSpins=True,
            initialLeftForC=True,
            name=None,
            audioFilesJson='{"files": []}',
        )
        self.goodSequence = Sequence.objects.create(
            transitionsJson='',
            transitionsCount=0,
            ratingsCount=RATINGS_COUNT_REQUIREMENT + 1,
            ratingsAverage=RATINGS_AVERAGE_REQUIREMENT + 0.5,
            level=LevelAbbreviation.ADULT_SILVER.value,
            isStep=True,
            hasJumps=False,
            hasSpins=True,
            initialLeftForC=True,
            name=None,
            audioFilesJson='{"files": []}',
        )
        self.newSequence = Sequence.objects.create(
            transitionsJson='',
            transitionsCount=0,
            ratingsCount=RATINGS_COUNT_REQUIREMENT - 1,
            ratingsAverage=RATINGS_AVERAGE_REQUIREMENT + 0.5,
            level=LevelAbbreviation.ADULT_SILVER.value,
            isStep=True,
            hasJumps=False,
            hasSpins=True,
            initialLeftForC=True,
            name=None,
            audioFilesJson='{"files": []}',
        )

    def testParentSequences(self):
        result = list(parentSequences(LevelAbbreviation.ADULT_SILVER.value, True))
        self.assertEqual(len(result), 3)

        hasFirstPrimary = [s for s in result if s.id == self.primarySequence1.id]
        hasSecondPrimary = [s for s in result if s.id == self.primarySequence2.id]
        hasGoodSequence = [s for s in result if s.id == self.goodSequence.id]

        self.assertFalse(hasFirstPrimary == [])
        self.assertFalse(hasSecondPrimary == [])
        self.assertFalse(hasGoodSequence == [])

