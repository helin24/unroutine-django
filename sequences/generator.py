import json
import random
from .models import Edge, Transition, EdgeWithFoot, TransitionWithFoot, Sequence, Move
from django.db.models import Sum, Q
from sequences.utils import transitionMap, parentSequences
from .constants import LevelAbbreviation
from sequences.audio_manager import AudioManager

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

    def makeFromDatabase(self, steps, cw, stepSequence, level, minId):
        sequence = Sequence.objects.filter(transitionsCount__gte=steps, isStep=stepSequence, level=level, id__gte=minId).first()
        if sequence is None:
            # Generate sequence
            sequence = self.makeNewGenetic(steps, cw, stepSequence, level)
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

        if steps < len(objects):
            randStart = random.randint(0, len(objects) - steps)
            end = randStart + steps
        else:
            randStart = 0
            end = len(objcts)

        transitionsWithFoot = transitionsWithFoot[randStart:end]

        # look for audio
        audioUrl = AudioManager().getSequenceUrl(sequence, transitionsWithFoot, cw, randStart, end - 1)

        startEdge = transitionsWithFoot[0].entry

        return {'transitions': transitionsWithFoot, 'startEdge': startEdge, 'steps': len(transitions), 'clockwise': cw, 'id': sequence.id, 'audio': audioUrl}

    def makeNewGenetic(self, steps, cw, stepSequence, level):
        # find sequences that are this level and step sequence
        transitionsWithFoot = map(lambda s: self.transitionsWithFootFromSequence(s, cw), parentSequences(level, stepSequence))

        moveFrequencies = self.getMoveFrequencies(stepSequence, level)

        sequencesWithChiSquare = []
        maxChiSquare = 0
        totalChiSquare = 0
        # get chi square values
        for sequence in transitionsWithFoot:
            chiSquare = self.getChiSquare(sequence, moveFrequencies)
            totalChiSquare += chiSquare
            maxChiSquare = max(chiSquare, maxChiSquare)
            sequencesWithChiSquare.append((sequence, chiSquare))

        resultingTransitionsWithFoot = self.runAlgorithm(sequencesWithChiSquare, (maxChiSquare + totalChiSquare / len(sequencesWithChiSquare)) / 2, moveFrequencies)

        canonicalTransitions = []
        hasJumps = False
        hasSpins = False
        for t in resultingTransitionsWithFoot:
            if t.move.category == 'J':
                hasJumps = True
            elif t.move.category == 'S':
                hasSpins = True
            canonicalTransitions.append(transitionMap(t))

        sequence = Sequence(
            transitionsCount=len(canonicalTransitions),
            transitionsJson = json.dumps({'transitions': canonicalTransitions}),
            level=level,
            isStep = stepSequence,
            hasJumps=hasJumps,
            hasSpins=hasSpins,
            initialLeftForC=((resultingTransitionsWithFoot[0].entry.foot == 'L') == cw)
        )
        sequence.save()

        return sequence

    def makeFromGenetic(self, cw, stepSequence, level):
        sequence = self.makeNewGenetic(10, cw, stepSequence, level)
        transitionsWithFoot = self.transitionsWithFootFromSequence(sequence, cw)
        return {'transitions': transitionsWithFoot, 'startEdge': transitionsWithFoot[0].entry, 'steps': len(transitionsWithFoot), 'clockwise': cw, 'id': sequence.id}

    def getChiSquare(self, sequence, moveFrequencies):
        # sequence is list of transitionsWithFoot
        sumSquares = 0.0

        sequenceMap = {}
        for t in sequence:
            if t.move.abbreviation not in sequenceMap:
                sequenceMap[t.move.abbreviation] = 0
            sequenceMap[t.move.abbreviation] += 1

        for moveAbbr, frequency in moveFrequencies.items():
            if frequency > 0:
                sumSquares += ((frequency * len(sequence) - sequenceMap.get(moveAbbr, 0) * 1.0) ** 2 / (frequency * len(sequence)))

        return sumSquares


    def getMoveFrequencies(self, stepSequence, level):
        label = None
        stepWord = 'step' if stepSequence else 'nonstep'
        if level == LevelAbbreviation.ADULT_BRONZE.value:
            label = f'frequency_adult_bronze_{stepWord}'
        elif level == LevelAbbreviation.ADULT_SILVER.value:
            label = f'frequency_adult_silver_{stepWord}'
        elif level == LevelAbbreviation.ADULT_GOLD.value:
            label = f'frequency_adult_gold_{stepWord}'

        if label is None:
            raise Exception(f'Level {level} could not be found')

        totalMoves = Move.objects.aggregate(Sum(label))[f'{label}__sum']

        moveFrequencies = {}
        for move in Move.objects.all().iterator():
            moveFrequencies[move.abbreviation] = getattr(move, label) * 1.0 / totalMoves

        return moveFrequencies


    def runAlgorithm(self, sequencesPopulation, chiSquareTarget, moveFrequencies):
        if len(sequencesPopulation) < 3:
            raise Exception('The population is not large enough')

        generated = []
        attempts = 0
        while attempts < 5:
            attempts += 1
            # select two sequences randomly from transitions as tournament (select 3 first and drop worst one)
            threeSequences = sorted(random.sample(sequencesPopulation, 3), key=lambda s: s[1])

            first = threeSequences[0][0]
            second = threeSequences[1][0]

            # combine the two
            randomLength = random.randint(4, 8)
            if len(first) < randomLength:
                start = 0
                end = len(first)
            else:
                start = random.randint(0, len(first) - randomLength)
                end = start + randomLength
            first = first[start:end]

            endEdge = first[-1].exit

            potentialStarts = self.findMatchingTransitionIdxs(second, endEdge)
            if not potentialStarts:
                continue
            randomStartIdx = random.choice(potentialStarts)
            randomEndIdx = min(randomStartIdx + random.randint(4, 8), len(second))

            first.extend(second[randomStartIdx:randomEndIdx])

            first = self.maybeMutate(first)
            self.debugPrint(first)

            # calculate chi square - probably also need to pass in map
            chiSquare = self.getChiSquare(first, moveFrequencies)
            print(chiSquare)
            # if chi square is below target, return sequence
            if chiSquare < chiSquareTarget:
                return first

            # otherwise add to population?
            sequencesPopulation.append((first, chiSquare))
            generated.append((first, chiSquare))
        
        return sorted(generated, key=lambda s: s[1])[0]

    def debugPrint(self, transitionsWithFoot):
        for t in transitionsWithFoot:
            print('%s -> %s -> %s' % (t.entry, t.move.name, t.exit))
        print('')

    def maybeMutate(self, transitionsWithFoot):
        # based on length, give probability for each element? Or just select one element and mutate?
        mutateIdx = random.randint(0, len(transitionsWithFoot) - 1)
        mutateTransition = transitionsWithFoot[mutateIdx]
        newTransition = Transition.objects.filter(
            entry__abbreviation=mutateTransition.entry.abbreviation,
            exit__abbreviation=mutateTransition.exit.abbreviation,
            move__changeFoot=mutateTransition.move.changeFoot,
            move__initialLeftForC=mutateTransition.move.initialLeftForC
        ).order_by('?').first()

        transitionsWithFoot[mutateIdx] = TransitionWithFoot(newTransition, mutateTransition.entry.foot, mutateTransition.exit.foot)
        return transitionsWithFoot

    def findMatchingTransitionIdxs(self, transitions, edge):
        def matches(idx):
            entry = transitions[idx].entry
            return entry.foot == edge.foot and entry.abbreviation == edge.abbreviation

        return list(filter(matches, range(0, len(transitions))))

    def transitionsWithFootFromSequence(self, sequence, cw):
        decoded = json.loads(sequence.transitionsJson)
        transitionsObjects = decoded['transitions']
        startFoot = self.chooseStartingFoot(sequence.initialLeftForC, cw)
        transitions = []
        for t in transitionsObjects:
            transition = Transition.objects.filter(move__abbreviation=t['move']).filter(entry__abbreviation=t['entry']).filter(exit__abbreviation=t['exit']).first()
            if transition is None:
                return {'error': 'No transition found for: %s -> %s -> %s' % (t['entry'], t['move'], t['exit'])}
            transitions.append(transition)

        return self.transitionsWithFoot(transitions, startFoot)

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

