# +
import sys, os
sys.path.append(os.path.abspath('..'))
import numpy as np
import scipy.sparse as sp
from imports import ilpsetsystem as ilpss
from imports import readFile

def calculateSetEfficiencies(numNodes, chosenNodes, setSizes, sets):
    costEfficiencies = dict()
    cardinChosen = numNodes - len(chosenNodes)
    for i in range(len(sets)):
        costEfficiencies[i] = (sets[i]['weight'] / setSizes[i]) / cardinChosen
    return costEfficiencies

def getHeurSol(coverMatrix, k, sets, numNodes, weightUniverse = None):
    """
        Returns the Heuristic Solution calculated by a greedy approximation algorithm for the k - coverage Problem.
        
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
    if weightUniverse == None:
        universe = set(i for i in range(numNodes))
    else:
        universe = weightUniverse
    chosenSets = []
    costEfficiencies = dict()
    containingSets = dict()
    chosenNodes = set()
    numSets = len(sets)
    numNodes = len(universe)
    setSizes = np.zeros(numSets)
    containedNodes = dict()

    

    for i in range(len(coverMatrix)):
        # Set of the Nodes that are contained in the current solution. Important set that determines
        containingSets[i] = set()
        for j in range (len(coverMatrix[i])):
            if ( i == 0):
                containedNodes[j] = set()
            if coverMatrix[i][j] > 0:
                containingSets[i].add(j)
                setSizes[j] += 1
                containedNodes[j].add(i)

    setSizes = setSizes.tolist()

    while universe != chosenNodes:
        costEff = calculateSetEfficiencies(numNodes, chosenNodes, setSizes, sets)
        for i in range(len(sets)):
            if i in chosenSets:
                costEff[i] = 10000
        minSet = min(costEff.keys(), key=(lambda k: costEff[k]))
        chosenNodes = containedNodes[minSet].union(chosenNodes)
        chosenSets.append(minSet)
        if (k <= len(chosenSets)):
            break
    return chosenSets, chosenNodes
