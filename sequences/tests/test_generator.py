from django.test import TestCase
from sequences.models import Move, Edge, Transition, TransitionWithFoot, EdgeWithFoot
from sequences.generator import Generator

class GeneratorTestCase(TestCase):
    def setUp(self):
        move = Move.objects.create(name="Three Turn", abbreviation="3Turn", changeFoot=False, initialLeftForC=None)
        tlMove = Move.objects.create(name="Toe Loop", abbreviation="TL", changeFoot=False, initialLeftForC=True)
        salMove = Move.objects.create(name="Salchow", abbreviation="Sal", changeFoot=True, initialLeftForC=False)
        stepMove = Move.objects.create(name="Step", abbreviation="step", changeFoot=True, initialLeftForC=None)

        foEdge = Edge.objects.create(name="Forward Outside", abbreviation="FO")
        self.foEdge = foEdge
        fiEdge = Edge.objects.create(name="Forward Inside", abbreviation="FI")
        biEdge = Edge.objects.create(name="Back Inside", abbreviation="BI")
        boEdge = Edge.objects.create(name="Back Outside", abbreviation="BO")

        self.transition = Transition.objects.create(move=move, entry=foEdge, exit=biEdge)
        self.tlTransition = Transition.objects.create(move=tlMove, entry=boEdge, exit=boEdge)
        self.boTurnTransition = Transition.objects.create(move=move, entry=boEdge, exit=fiEdge)
        self.salTransition = Transition.objects.create(move=salMove, entry=biEdge, exit=boEdge)
        self.stepTransition = Transition.objects.create(move=stepMove, entry=fiEdge, exit=foEdge)


    def testNextClockwiseIfInitialLeft(self):
        # Start - on initial foot, no directional moves yet + non-directional transition
        start = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=None, transition=self.transition)
        self.assertEqual(start, None)

        # On initial foot, no directional moves yet + directional transition
        tl = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=None, transition=self.tlTransition)
        self.assertEqual(tl, True)

        sal = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=None, transition=self.salTransition)
        self.assertEqual(sal, False)


        # Start - not on initial foot, no directional moves yet + non-directional transition
        start = Generator().nextClockwiseIfInitialLeft(onInitialFoot=False, clockwiseIfInitialLeft=None, transition=self.transition)
        self.assertEqual(start, None)

        # Not on initial foot, no directional moves yet + directional transition
        tl = Generator().nextClockwiseIfInitialLeft(onInitialFoot=False, clockwiseIfInitialLeft=None, transition=self.tlTransition)
        self.assertEqual(tl, False)

        sal = Generator().nextClockwiseIfInitialLeft(onInitialFoot=False, clockwiseIfInitialLeft=None, transition=self.salTransition)
        self.assertEqual(sal, True)


        # On initial foot, True for clockwiseIfInitialLeft + non-directional transition
        boTurn = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=True, transition=self.boTurnTransition)
        self.assertEqual(boTurn, True)

        # On initial foot, True for clockwiseIfInitialLeft + directional transition
        tl = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=True, transition=self.tlTransition)
        self.assertEqual(tl, True)

        # TODO: Maybe this shouldn't happen?
        tl = Generator().nextClockwiseIfInitialLeft(onInitialFoot=True, clockwiseIfInitialLeft=True, transition=self.salTransition)
        self.assertEqual(tl, True)

    def testInitialLeftForCToExclude(self):
        self.assertEqual(Generator().initialLeftForCToExclude(True, None), None)
        self.assertEqual(Generator().initialLeftForCToExclude(True, True), False)
        self.assertEqual(Generator().initialLeftForCToExclude(True, False), True)

        self.assertEqual(Generator().initialLeftForCToExclude(False, None), None)
        self.assertEqual(Generator().initialLeftForCToExclude(False, True), True)
        self.assertEqual(Generator().initialLeftForCToExclude(False, False), False)

    def testChooseStartingFoot(self):
        self.assertEqual(Generator().chooseStartingFoot(clockwiseIfInitialLeft=None, cw=True), 'L')
        self.assertEqual(Generator().chooseStartingFoot(clockwiseIfInitialLeft=True, cw=True), 'L')
        self.assertEqual(Generator().chooseStartingFoot(clockwiseIfInitialLeft=False, cw=True), 'R')

        self.assertEqual(Generator().chooseStartingFoot(clockwiseIfInitialLeft=None, cw=False), 'L')
        self.assertEqual(Generator().chooseStartingFoot(clockwiseIfInitialLeft=True, cw=False), 'R')
        self.assertEqual(Generator().chooseStartingFoot(clockwiseIfInitialLeft=False, cw=False), 'L')

    def testTransitionsWithFoot(self):
        transitions = [self.transition, self.salTransition, self.tlTransition]

        result = Generator().transitionsWithFoot(transitions, 'R')

        self.assertEqual(result[0].entry.abbreviation, 'FO')
        self.assertEqual(result[0].entry.foot, 'R')
        self.assertEqual(result[0].exit.abbreviation, 'BI')
        self.assertEqual(result[0].exit.foot, 'R')

        self.assertEqual(result[1].entry.abbreviation, 'BI')
        self.assertEqual(result[1].entry.foot, 'R')
        self.assertEqual(result[1].exit.abbreviation, 'BO')
        self.assertEqual(result[1].exit.foot, 'L')

        self.assertEqual(result[2].entry.abbreviation, 'BO')
        self.assertEqual(result[2].entry.foot, 'L')
        self.assertEqual(result[2].exit.abbreviation, 'BO')
        self.assertEqual(result[2].exit.foot, 'L')

    def testFindMatchingTransitionIdxs(self):
        transitions = [self.transition, self.salTransition, self.tlTransition, self.boTurnTransition, self.stepTransition, self.transition]
        # RFO -> RBI -> LBO -> LBO -> LFI -> RFO -> RBI
        transitionsWithFoot = Generator().transitionsWithFoot(transitions, 'R')
        edge = EdgeWithFoot(self.foEdge, 'R')

        matchingIdxs = Generator().findMatchingTransitionIdxs(transitionsWithFoot, edge)
        self.assertEqual(len(matchingIdxs), 2)
        self.assertEqual(matchingIdxs[0], 0)
        self.assertEqual(matchingIdxs[1], 5)

