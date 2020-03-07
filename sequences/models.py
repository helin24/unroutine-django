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

    def __str__(self):
        return self.name

class Edge(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return self.name

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

