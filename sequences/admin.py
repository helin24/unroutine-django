from django.contrib import admin

# Register your models here.
from .models import Edge, Move, Transition

class EdgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation')

class MoveAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'category')

class TransitionAdmin(admin.ModelAdmin):
    list_display = ('move', 'entry', 'exit')

admin.site.register(Edge, EdgeAdmin)
admin.site.register(Move, MoveAdmin)
admin.site.register(Transition, TransitionAdmin)
