from django.shortcuts import render
from django.http import HttpResponse
from .models import Edge, Transition

# Create your views here.
def index(request):
    # find all moves and select one at random
    # find what edge it ends on
    # find a move that starts on that one and continue
    current = Transition.objects.order_by("?").first()
    sequence = [current]
    count = 1
    while count < 5:
        current = Transition.objects.filter(entry=current.exit.id).order_by("?").first()
        sequence.append(current)
        count += 1

    return HttpResponse(sequence[0].entry.abbreviation + " -> " +  " -> ".join(x.move.abbreviation for x in sequence) + " -> " + sequence[-1].exit.abbreviation)
