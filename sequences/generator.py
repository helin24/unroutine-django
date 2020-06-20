from .models import Edge, Transition, EdgeWithFoot

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

        """
        currentFootIsLeft = result['startFoot'] == 'L'
        transitionsWithFoot = []
        for transition in result['transitions']:
            if transition.move.changeFoot == currentFootIsLeft:
                currentFootIsLeft = False
            else:
                currentFootIsLeft = True
    
            transitionsWithFoot.append({'transition': transition, 'foot': 'L' if currentFootIsLeft else 'R'})
    
        result['transitions'] = transitionsWithFoot
        """

        startEdge = EdgeWithFoot(sequence[0].entry, startFoot)

        return {'transitions': sequence, 'startEdge': startEdge, 'steps': steps, 'clockwise': cw, 'startFoot': startFoot}

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

