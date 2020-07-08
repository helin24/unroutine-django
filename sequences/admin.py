from django.contrib import admin

# Register your models here.
from .models import Edge, Move, Transition, Sequence

class EdgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation')

class MoveAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'category', 'changeFoot', 'initialLeftForC', 'frequency', 'frequency_adult_gold_step', 'frequency_adult_gold_nonstep', 'frequency_adult_silver_step', 'frequency_adult_silver_nonstep', 'frequency_adult_bronze_step', 'frequency_adult_bronze_nonstep')

class TransitionAdmin(admin.ModelAdmin):
    list_display = ('move', 'entry', 'exit')

class SequenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'transitionsCount', 'ratingsCount', 'ratingsAverage', 'level', 'isStep', 'hasJumps', 'hasSpins', 'initialLeftForC')

admin.site.register(Edge, EdgeAdmin)
admin.site.register(Move, MoveAdmin)
admin.site.register(Transition, TransitionAdmin)
admin.site.register(Sequence, SequenceAdmin)
