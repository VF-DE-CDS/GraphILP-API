# +
import sys, os
sys.path.append(os.path.abspath('..'))
import numpy as np
import scipy.sparse as sp
from imports import ilpsetsystem as ilpss
from covering import set_packing as setp

def calculateSetEfficiencies(numNodes, chosenNodes, setSizes, sets):
    costEfficiencies = dict()
    cardinChosen = numNodes - len(chosenNodes)
    for i in range(len(sets)):
        costEfficiencies[i] = sets[i]['weight'] / cardinChosen
    return costEfficiencies

path ="/home/tsauter/GraphILP/GraphILP-API/graphilp/examples/setcoverTestInstances/scpd1.txt"
chosenSets = []
costEfficiencies = dict()
containingSets = dict()
chosenNodes = set()
numSets = 3
numNodes = 3
setSizes = np.zeros(numSets)
containedNodes = dict()

cover_matrix = np.array([[ 0.,  0.,   1],
       [ 1,  0.,  0.],
       [ 0.,  1,  1]])
sets = {0:{'weight': 4},1:{'weight': 2},2:{'weight': 1}}
universe = {0, 1, 2}



for i in range(len(cover_matrix)):
    # Set of the Nodes that are contained in the current solution. Important set that determines
    containingSets[i] = set()
    for j in range (len(cover_matrix[i])):
        if ( i == 0):
            containedNodes[j] = set()
        if cover_matrix[i][j] > 0:
            containingSets[i].add(j)
            setSizes[j] += 1
            containedNodes[j].add(i)

setSizes = setSizes.tolist() 
print(containedNodes)

while universe != chosenNodes:
    costEff = calculateSetEfficiencies(numNodes, chosenNodes, setSizes, sets)
    for i in range(len(sets)):
        if i in chosenSets:
            costEff[i] = 10000
    minSet = min(costEff.keys(), key=(lambda k: costEff[k]))
    
    chosenNodes = containedNodes[minSet].union(chosenNodes)
    chosenSets.append(minSet)
    
print(chosenSets)


# -




