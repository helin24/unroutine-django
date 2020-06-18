from django.db import models

# Create your models here.
class Move(models.Model):
    CATEGORY_CHOICES = [
        ('J', 'Jump'),
        ('S', 'Spin'),
        ('M', 'Move'),
    ]
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

