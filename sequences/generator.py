from .models import Edge, Transition, EdgeWithFoot, TransitionWithFoot, Sequence
import json
import random

REPEATABLE = set(['TL', 'Loop', 'Bunny Hop'])
MOVES_BEFORE_BACKSPIN = set(['FScSpin', 'FSitSpin', 'FCaSpin', 'FLbSpin', '3Turn'])
BACKSPINS = set(['BScSpin', 'BSitSpin', 'BCaSpin'])

class Generator:
    def __init__(self):
        self.data = []

    def makeRandom(self, request, steps, cw):
        onInitialFoot = True
    
        # TODO: If testing, move this to other class and mock?
        availableTransitions = Transition.objects.select_related('move', 'entry', 'exit')
        current = availableTransitions.order_by('?').first()
    
        clockwiseIfInitialLeft = None
        if current.move.initialLeftForC is not None:
            clockwiseIfInitialLeft = current.move.initialLeftForC
    
        onInitialFoot = not current.move.changeFoot
    
        """
        Example - first move is salchow - change foot true and initialIsLeftForC false
        endsOnInitialFoot = false
        Need to save that if initial foot is left, this is CCW
        """

        sequence = [current]
        count = 1

        while count < steps:
            # find what edge it ends on
            # find a move that starts on that one and continue
            query = availableTransitions.filter(entry=current.exit.id)

            # Exclude the same move unless it's repeatable
            if current.move.abbreviation not in REPEATABLE:
                query = query.exclude(id=current.id)
    
            # Exclude backspins unless preceded by particular moves
            if current.move.abbreviation not in MOVES_BEFORE_BACKSPIN:
                query = query.exclude(move__abbreviation__in=BACKSPINS)

            # Exclude directional moves that don't align with left and initial
            initialLeftForCToExclude = self.initialLeftForCToExclude(onInitialFoot, clockwiseIfInitialLeft)
            if initialLeftForCToExclude is not None:
                query = query.exclude(move__initialLeftForC=initialLeftForCToExclude)
    
            current = query.order_by("?").first()

            clockwiseIfInitialLeft = self.nextClockwiseIfInitialLeft(onInitialFoot, clockwiseIfInitialLeft, current)
            onInitialFoot = onInitialFoot is not current.move.changeFoot

            sequence.append(current)
            count += 1

        startFoot = self.chooseStartingFoot(clockwiseIfInitialLeft, cw)

        transitions = self.transitionsWithFoot(sequence, startFoot)

        startEdge = transitions[0].entry

        return {'transitions': transitions, 'startEdge': startEdge, 'steps': steps, 'clockwise': cw}

    def makeFromDatabase(self, cw):
        sequence = Sequence.objects.first()
        decoded = json.loads(sequence.transitionsJson)
        objects = decoded['transitions']
        transitions = []
        for t in objects:
            transition = Transition.objects.filter(move__abbreviation=t['move']).filter(entry__abbreviation=t['entry']).filter(exit__abbreviation=t['exit']).first()
            if transition is None:
                raise Exception('No transition found for: %s -> %s -> %s' % (t['entry'], t['move'], t['exit']))
            transitions.append(transition)

        startFoot = self.chooseStartingFoot(sequence.initialLeftForC, cw)
        transitionsWithFoot = self.transitionsWithFoot(transitions, startFoot)
        startEdge = transitionsWithFoot[0].entry

        return {'transitions': transitionsWithFoot, 'startEdge': startEdge, 'steps': len(transitions), 'clockwise': cw, 'id': sequence.id}

    def makeFromGenetic(self, cw, stepSequence, level):
        # find sequences that are this level and step sequence
        randomQuery = Sequence.objects.filter(isStep=stepSequence, level=level, name__isnull=False).order_by('?')
        first = randomQuery.first()
        second = randomQuery.exclude(pk=first.id).first()
        if second is None:
            return {}

        randomCutoff = random.randint(4, 8)

        # Assign foot for each transition
        decoded = json.loads(first.transitionsJson)
        transitionsObjects = decoded['transitions'][:randomCutoff]
        startFoot = self.chooseStartingFoot(first.initialLeftForC, cw)
        transitions = []
        for t in transitionsObjects:
            transition = Transition.objects.filter(move__abbreviation=t['move']).filter(entry__abbreviation=t['entry']).filter(exit__abbreviation=t['exit']).first()
            if transition is None:
                raise Exception('No transition found for: %s -> %s -> %s' % (t['entry'], t['move'], t['exit']))
            transitions.append(transition)

        transitionsWithFoot = self.transitionsWithFoot(transitions, startFoot)

        secondDecoded = json.loads(second.transitionsJson)
        secondObjects = secondDecoded['transitions']
        secondStartFoot = self.chooseStartingFoot(second.initialLeftForC, cw)
        secondTransitions = []
        for t in secondObjects:
            transition = Transition.objects.filter(move__abbreviation=t['move']).filter(entry__abbreviation=t['entry']).filter(exit__abbreviation=t['exit']).first()
            if transition is None:
                raise Exception('No transition found for: %s -> %s -> %s' % (t['entry'], t['move'], t['exit']))
            secondTransitions.append(transition)

        secondTransitionsWithFoot = self.transitionsWithFoot(secondTransitions, startFoot)

        # join somewhere in there
        endEdge = transitionsWithFoot[-1].exit

        firstIdx = None
        for idx in range(0, len(secondTransitionsWithFoot)):
            transition = secondTransitionsWithFoot[idx]
            if transition.entry.foot == endEdge.foot and transition.entry.abbreviation == endEdge.abbreviation:
                firstIdx = idx
                break

        if firstIdx == None:
            for t in transitionsWithFoot:
                print('%s -> %s -> %s' % (t.entry, t.move.name, t.exit))
            print(' ')
            for t in secondTransitionsWithFoot:
                print('%s -> %s -> %s' % (t.entry, t.move.name, t.exit))
            raise Exception('No matching transition found to join %s and %s with %s' % (first.id, second.id, endEdge))

        for offset in range(0, 5):
            transitionsWithFoot.append(secondTransitionsWithFoot[firstIdx + offset])

        for t in transitionsWithFoot:
            print('%s -> %s -> %s' % (t.entry, t.move.name, t.exit))

        # save to database
        # send for rating
        return {}


    def transitionsWithFoot(self, transitions, startFoot):
        currentFootIsLeft = startFoot == 'L'

        transitionsWithFoot = []
        for transition in transitions:
            entryFoot = 'L' if currentFootIsLeft else 'R'

            if transition.move.changeFoot == currentFootIsLeft:
                currentFootIsLeft = False
            else:
                currentFootIsLeft = True

            exitFoot = 'L' if currentFootIsLeft else 'R'

            transitionsWithFoot.append(TransitionWithFoot(transition, entryFoot, exitFoot))

        return transitionsWithFoot

    def chooseStartingFoot(self, clockwiseIfInitialLeft, cw):
        if clockwiseIfInitialLeft is None:
            return 'L'
        elif clockwiseIfInitialLeft == cw:
            return 'L'
        else:
            return 'R'

    def nextClockwiseIfInitialLeft(self, onInitialFoot, clockwiseIfInitialLeft, transition):
        # if we've already switched feet, then current move initialLeftForC should be reversed
        if clockwiseIfInitialLeft is None and transition.move.initialLeftForC is not None:
            return onInitialFoot == transition.move.initialLeftForC
        return clockwiseIfInitialLeft

    def initialLeftForCToExclude(self, onInitialFoot, clockwiseIfInitialLeft):
        # If there is no directionality yet, return None
        if clockwiseIfInitialLeft is None:
            return None

        # If directionality has been established, then we want to check:
        # 1. Are we on the initial foot? If so, exclude moves that do not match the established direction
        if onInitialFoot:
            return not clockwiseIfInitialLeft
        else:
            return clockwiseIfInitialLeft

