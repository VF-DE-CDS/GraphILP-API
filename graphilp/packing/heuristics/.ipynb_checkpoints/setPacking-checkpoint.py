# +
import sys, os
sys.path.append(os.path.abspath('..'))
import numpy as np
import scipy.sparse as sp
from imports import ilpsetsystem as ilpss
from imports import readFile
import time

def calculateSetEfficiencies(chosenSets, setSizes, sets):
    costEfficiencies = dict()
    for i, (key, value) in enumerate(sets.items()):
        costEfficiencies[key] = setSizes[key] / sets[key]['weight']
    return costEfficiencies

def removeSets(sets, chosenNodes, containedNodes):
    setsToPop = set()
    for curSet in sets:
        for node in chosenNodes:
            if node in containedNodes[curSet]:
                setsToPop.add(curSet)
                break
    for curSet in setsToPop:
        sets.pop(curSet)
    return sets

def getHeurSol(coverMatrix, sets, numNodes):
    """
        Returns the Heuristic Solution calculated by a greedy approximation algorithm for the set Packing Problem.
        
        :param coverMatrix: Cover / Incidence Matrix defining the edges of the Graph
        :param k: Maximum Sets to use
        :param sets: Sets that cover Nodes
        :params universe: List of Nodes
        :type coverMatrix: List of List
        :type k: int
        :type sets: Dict of int:dict. The value needs to specifiy a weight.
        :type universe: list of int
        :rtype: chosen Sets as list of indeces
    """
    
    chosenSets = []
    costEfficiencies = dict()
    containingSets = dict()
    chosenNodes = set()
    numSets = len(sets)
    setSizes = np.zeros(numSets)
    containedNodes = dict()
    universe = set(i for i in range(numNodes))
    setsCopy = dict.copy(sets)

    for i in range(len(coverMatrix)):
        containingSets[i] = set()
        for j in range (len(coverMatrix[i])):
            if (i == 0):
                containedNodes[j] = set()
            if coverMatrix[i][j] > 0:
                containingSets[i].add(j)
                setSizes[j] += 1
                containedNodes[j].add(i)

    setSizes = setSizes.tolist()
    while sets != {}:
        costEff = calculateSetEfficiencies(chosenSets, setSizes, sets)
        minSet = min(costEff.keys(), key=(lambda k: costEff[k]))
        chosenNodes = containedNodes[minSet].union(chosenNodes)
        chosenSets.append(minSet)
        sets = removeSets(sets, chosenNodes, containedNodes)
    return chosenSets, chosenNodes
