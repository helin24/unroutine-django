from django.test import TestCase
from sequences.models import Move, Edge, Transition
from sequences.generator import Generator

class GeneratorTestCase(TestCase):
    def setUp(self):
        move = Move.objects.create(name="Three Turn", abbreviation="3Turn", changeFoot=False, initialLeftForC=None)
        foEdge = Edge.objects.create(name="Forward Outside", abbreviation="FO")
        biEdge = Edge.objects.create(name="Back Inside", abbreviation="BO")
        self.transition = Transition.objects.create(move=move, entry=foEdge, exit=biEdge)

    def testNextClockwiseIfInitialLeft(self):
        start = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=None, transition=self.transition)
        self.assertEquals(start, None)

