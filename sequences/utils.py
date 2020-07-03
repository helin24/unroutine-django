def sequenceNameFromRoutineFeatures(level, routineNumber, inRoutineLetter):
    return '%s_%s_%s' % (level, routineNumber, inRoutineLetter)

def transitionMap(transition):
    return {
        'move': transition.move.abbreviation,
        'entry': transition.entry.abbreviation,
        'exit': transition.exit.abbreviation,
    }

