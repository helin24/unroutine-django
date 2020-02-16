from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
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

    template = loader.get_template('sequences/index.html')
    context = {'transitions': sequence, 'startEdge': sequence[0].entry}
    return HttpResponse(template.render(context, request))

