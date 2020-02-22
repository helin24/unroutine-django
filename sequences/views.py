from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Edge, Transition

REPEATABLE = set(['TL', 'Loop', 'Bunny Hop'])
MOVES_BEFORE_BACKSPIN = set(['FScSpin', 'FSitSpin', 'FCaSpin', 'FLbSpin', '3Turn'])
BACKSPINS = set(['BScSpin', 'BSitSpin', 'BCaSpin'])

# Create your views here.
def index(request):
    steps = 5
    cw = False
    if request.POST:
        steps = min(20, int(request.POST['steps']))
        if 'clockwise' in request.POST:
            cw = request.POST['clockwise'] == 'on'
    excludeDirection = 'CCW' if cw else 'CW'

    # find all moves and select one at random
    availableTransitions = Transition.objects.exclude(rotationDirection=excludeDirection)
    current = availableTransitions.order_by("?").first()
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

        current = query.order_by("?").first()
        sequence.append(current)
        count += 1

    template = loader.get_template('sequences/index.html')
    context = {'transitions': sequence, 'startEdge': sequence[0].entry, 'steps': steps, 'clockwise': cw}
    return HttpResponse(template.render(context, request))

