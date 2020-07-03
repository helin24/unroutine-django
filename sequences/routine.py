from sequences.models import Move, Edge, Transition
from sequences.constants import CATEGORY_CHOICES
import csv
import os

def getSequenceSegment(level, stepSequence):
    # TODO: Eventually need to consider number of transitions

    # Find all files of that level
    # Find all files matching stepSequence
    # Choose another routine that has matching initialLeftForC or reverse if 

    # Example - one is (L)BO, Step -> RFO, Axel -> BO (initialLeftForC = true)
    # BO, Step -> FO, Axel -> BO
    # another is (L)BO, Step -> RFI, 3Turn -> RBO, TL -> RBO (initialLeftForC = false)
    # BO, Step -> FI, 3Turn -> BO, TL -> BO
    # These two can't be connected unless the second one is flipped to make sure initial foot is different in second one
    # Can make LBO, Step -> RFO, Axel -> LBO and connect with RBO, Step -> LFI, 3Turn -> LBO, TL -> LBO
