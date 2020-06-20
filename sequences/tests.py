from django.test import TestCase
from sequences.models import Move, Edge, Transition
from sequences.generator import Generator

class GeneratorTestCase(TestCase):
    def setUp(self):
        move = Move.objects.create(name="Three Turn", abbreviation="3Turn", changeFoot=False, initialLeftForC=None)
        tlMove = Move.objects.create(name="Toe Loop", abbreviation="TL", changeFoot=False, initialLeftForC=True)
        salMove = Move.objects.create(name="Salchow", abbreviation="Sal", changeFoot=True, initialLeftForC=False)

        foEdge = Edge.objects.create(name="Forward Outside", abbreviation="FO")
        fiEdge = Edge.objects.create(name="Forward Inside", abbreviation="FI")
        biEdge = Edge.objects.create(name="Back Inside", abbreviation="BI")
        boEdge = Edge.objects.create(name="Back Outside", abbreviation="BO")

        self.transition = Transition.objects.create(move=move, entry=foEdge, exit=biEdge)
        self.tlTransition = Transition.objects.create(move=tlMove, entry=boEdge, exit=boEdge)
        self.boTurnTransition = Transition.objects.create(move=move, entry=boEdge, exit=fiEdge)
        self.salTransition = Transition.objects.create(move=salMove, entry=biEdge, exit=boEdge)


    def testNextClockwiseIfInitialLeft(self):
        # Start - on initial foot, no directional moves yet + non-directional transition
        start = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=None, transition=self.transition)
        self.assertEquals(start, None)

        # On initial foot, no directional moves yet + directional transition
        tl = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=None, transition=self.tlTransition)
        self.assertEquals(tl, True)

        sal = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=None, transition=self.salTransition)
        self.assertEquals(sal, False)


        # Start - not on initial foot, no directional moves yet + non-directional transition
        start = Generator().nextClockwiseIfInitialLeft(onInitialFoot=False, clockwiseIfInitialLeft=None, transition=self.transition)
        self.assertEquals(start, None)

        # Not on initial foot, no directional moves yet + directional transition
        tl = Generator().nextClockwiseIfInitialLeft(onInitialFoot=False, clockwiseIfInitialLeft=None, transition=self.tlTransition)
        self.assertEquals(tl, False)

        sal = Generator().nextClockwiseIfInitialLeft(onInitialFoot=False, clockwiseIfInitialLeft=None, transition=self.salTransition)
        self.assertEquals(sal, True)


        # On initial foot, True for clockwiseIfInitialLeft + non-directional transition
        boTurn = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=True, transition=self.boTurnTransition)
        self.assertEquals(boTurn, True)

        # On initial foot, True for clockwiseIfInitialLeft + directional transition
        tl = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=True, transition=self.tlTransition)
        self.assertEquals(tl, True)

        # TODO: Maybe this shouldn't happen?
        tl = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=True, transition=self.salTransition)
        self.assertEquals(tl, True)

    def testInitialLeftForCToExclude(self):
        self.assertEquals(Generator().initialLeftForCToExclude(True, None), None)
        self.assertEquals(Generator().initialLeftForCToExclude(True, True), False)
        self.assertEquals(Generator().initialLeftForCToExclude(True, False), True)

        self.assertEquals(Generator().initialLeftForCToExclude(False, None), None)
        self.assertEquals(Generator().initialLeftForCToExclude(False, True), True)
        self.assertEquals(Generator().initialLeftForCToExclude(False, False), False)

    def testChooseStartingFoot(self):
        self.assertEquals(Generator().chooseStartingFoot(clockwiseIfInitialLeft=None, cw=True), 'L')
        self.assertEquals(Generator().chooseStartingFoot(clockwiseIfInitialLeft=True, cw=True), 'L')
        self.assertEquals(Generator().chooseStartingFoot(clockwiseIfInitialLeft=False, cw=True), 'R')

        self.assertEquals(Generator().chooseStartingFoot(clockwiseIfInitialLeft=None, cw=False), 'L')
        self.assertEquals(Generator().chooseStartingFoot(clockwiseIfInitialLeft=True, cw=False), 'R')
        self.assertEquals(Generator().chooseStartingFoot(clockwiseIfInitialLeft=False, cw=False), 'L')

    def testTransitionsWithFoot(self):
        transitions = [self.transition, self.salTransition, self.tlTransition]

        result = Generator().transitionsWithFoot(transitions, 'R')

        self.assertEquals(result[0].entry.abbreviation, 'FO')
        self.assertEquals(result[0].entry.foot, 'R')
        self.assertEquals(result[0].exit.abbreviation, 'BI')
        self.assertEquals(result[0].exit.foot, 'R')

        self.assertEquals(result[1].entry.abbreviation, 'BI')
        self.assertEquals(result[1].entry.foot, 'R')
        self.assertEquals(result[1].exit.abbreviation, 'BO')
        self.assertEquals(result[1].exit.foot, 'L')

        self.assertEquals(result[2].entry.abbreviation, 'BO')
        self.assertEquals(result[2].entry.foot, 'L')
        self.assertEquals(result[2].exit.abbreviation, 'BO')
        self.assertEquals(result[2].exit.foot, 'L')

