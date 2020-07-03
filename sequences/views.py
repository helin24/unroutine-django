from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.core import serializers
from .models import Edge, Transition
from .generator import Generator

REPEATABLE = set(['TL', 'Loop', 'Bunny Hop'])
MOVES_BEFORE_BACKSPIN = set(['FScSpin', 'FSitSpin', 'FCaSpin', 'FLbSpin', '3Turn'])
BACKSPINS = set(['BScSpin', 'BSitSpin', 'BCaSpin'])

def index(request):
    steps = 5
    cw = False
    if request.POST:
        steps = min(20, int(request.POST['steps']))
        if 'clockwise' in request.POST:
            cw = request.POST['clockwise'] == 'on'
    template = loader.get_template('sequences/index.html')
    # This is if we want to generate from database
    # result = Generator().makeFromDatabase(cw)
    result = Generator().makeRandom(request, steps, cw)

    return HttpResponse(template.render(result, request))

def json(request):
    steps = 5
    cw = False
    if request.GET:
        steps = min(20, int(request.GET['steps']))
        if 'clockwise' in request.GET:
            cw = request.GET['clockwise'] == 'on'
    context = Generator().makeRandom(request, steps, cw)
    context['transitions'] = list(map(lambda t: t.toObject(), context['transitions']))
    context['startEdge'] = context['startEdge'].toObject()
    return JsonResponse(context, safe=False)

def generate(request):
    cw = True
    result = Generator().makeFromDatabase(cw)
    template = loader.get_template('sequences/generate.html')
    return HttpResponse(template.render(result, request))

def rate(request):
    rating = request.POST.get('rating')
    sequenceId = request.POST.get('sequenceId')
    print(rating, sequenceId)

    template = loader.get_template('sequences/rate.html')
    return HttpResponse(template.render({'rating': rating}, request))

