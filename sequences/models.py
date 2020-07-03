from django.db import models
from sequences.constants import CATEGORY_CHOICES, LEVEL_CHOICES

# Create your models here.
class Move(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=10, unique=True)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default='M')
    # True if for clockwise skaters, the move starts on the left foot.
    # False if it starts on the right foot.
    # Null if the move is not directional.
    initialLeftForC = models.BooleanField(null=True)
    # True if the move ends on the other foot.
    changeFoot = models.BooleanField(null=True)

    def __str__(self):
        return self.name

    def toObject(self):
        return {
            'name': self.name,
            'description': self.description,
            'abbreviation': self.abbreviation,
            'category': self.category,
            'initialLeftForC': self.initialLeftForC,
            'changeFoot': self.changeFoot,
        }

class Edge(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    def toObject(self):
        return {
            'name': self.name,
            'abbreviation': self.abbreviation,
        }

class EdgeWithFoot():
    def __init__(self, edge, foot):
        self.edge = edge
        self.name = edge.name
        self.abbreviation = edge.abbreviation
        self.foot = foot

    def __str__(self):
        return '%s%s' % (self.foot, self.abbreviation)

    def toObject(self):
        edge = self.edge.toObject()
        edge['foot'] = self.foot
        return edge

class Transition(models.Model):
    DIRECTION_CHOICES = [
        ('CW', 'Clockwise'),
        ('CCW', 'Counter-Clockwise'),
    ]
    move = models.ForeignKey(Move, on_delete=models.CASCADE)
    entry = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='entry')
    exit = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='exit')
    rotationDirection = models.CharField(max_length=3, choices=DIRECTION_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.entry.abbreviation + ' -> ' + self.move.abbreviation + ' -> ' + self.exit.abbreviation

    def toObject(self):
        return {
            'move': self.move.toObject(),
            'entry': self.entry.toObject(),
            'exit': self.exit.toObject(),
            'rotationDirection': self.rotationDirection,
        }

class TransitionWithFoot():
    def __init__(self, transition, entryFoot, exitFoot):
        self.transition = transition
        self.move = transition.move
        self.entry = EdgeWithFoot(transition.entry, entryFoot)
        self.exit = EdgeWithFoot(transition.exit, exitFoot)

    def toObject(self):
        transition = self.transition.toObject()
        transition['entry'] = self.entry.toObject()
        transition['exit'] = self.exit.toObject()
        return transition

class Sequence(models.Model):
    transitionsJson = models.TextField()
    transitionsCount = models.IntegerField()
    ratingsCount = models.IntegerField(default=0)
    ratingsAverage = models.DecimalField(null=True, blank=True, decimal_places=6, max_digits=7)
    level = models.CharField(max_length=5, choices=LEVEL_CHOICES, null=True, blank=True)
    isStep = models.BooleanField(default=False)
    hasJumps = models.BooleanField()
    hasSpins = models.BooleanField()
    initialLeftForC = models.BooleanField(null=True)
    name = models.CharField(max_length=50, null=True, blank=True)

