from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('json', views.json, name='json'),
    path('generate', views.generate, name='generate'),
    path('rate', views.rate, name='rate'),
    path('ratesequence', views.rateSequence, name='rateSequence'),
]
