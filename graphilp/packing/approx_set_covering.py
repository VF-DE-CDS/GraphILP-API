# +
import sys, os
sys.path.append(os.path.abspath('..'))
import numpy as np
import scipy.sparse as sp
from imports import ilpsetsystem as ilpss
from covering import set_packing as setp

def calculateSetEfficiencies(sets, chosenSets, setSizes):
    costEfficiencies = dict()
    cardChosen = len(sets) - len(chosenSets)
    for i in range(len(sets)):
        costEfficiencies[i] = sets[i]['weight'] / setSizes[i]
    return costEfficiencies

path ="/home/tsauter/GraphILP/GraphILP-API/graphilp/examples/setcoverTestInstances/scpd1.txt"
setSizes = dict()
setSize = 0
chosenSets = []
costEfficiencies = dict()
containedNodes = dict()
chosenNodes = set()

cover_matrix = np.array([[ 0.,  0.,   1],
       [ 1,  0.,  0.],
       [ 0.,  1,  1]])
sets = {0:{'weight': 4},1:{'weight': 2},2:{'weight': 1}}
universe = {0, 1, 2}



for i in range(len(cover_matrix)):
    # Set of the Nodes that are contained in the current solution. Important set that determines
    containedNodes[i] = set()
    for j in range (len(cover_matrix[i])):
        if cover_matrix[i][j] > 0:
            setSize = setSize + 1
            containedNodes[i].add(j)
    setSizes[i] = setSize
    setSize = 0
  
while universe != chosenNodes:
    costEff = calculateSetEfficiencies(sets, chosenSets, setSizes)
    for i in range(len(sets)):
        if i in chosenSets:
            costEff[i] = 10000
    minSet = min(costEff.keys(), key=(lambda k: costEff[k]))
    chosenNodes = containedNodes[minSet].union(chosenNodes)
    chosenSets.append(minSet)
    
print(chosenSets)


# -




