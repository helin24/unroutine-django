from django.db import models

# Create your models here.
class Move(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Edge(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Transition(models.Model):
    move = models.ForeignKey(Move, on_delete=models.CASCADE)
    entry = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='entry')
    exit = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='exit')

    def __str__(self):
        return self.entry.abbreviation + ' -> ' + self.move.abbreviation + ' -> ' + self.exit.abbreviation

