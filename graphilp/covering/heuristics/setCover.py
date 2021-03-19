# +
import sys, os
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../..'))
import numpy as np
import scipy.sparse as sp
from imports import ilpsetsystem as ilpss

def calculateSetEfficiencies(numNodes, chosenNodes, setSizes, sets):
    costEfficiencies = dict()
    cardinChosen = numNodes - len(chosenNodes)
    
    for i in range(len(sets)):
        costEfficiencies[i] = (sets[i]['weight'] / setSizes[i]) / cardinChosen
    return costEfficiencies

def getHeurSol(coverMatrix, sets, numNodes):
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
    
    chosenSets = []
    costEfficiencies = dict()
    containingSets = dict()
    chosenNodes = set()
    numSets = len(sets)
    setSizes = np.zeros(numSets)
    containedNodes = dict()
    universe = set(i for i in range(numNodes))
    

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
    return chosenSets

if __name__ == '__main__':
    getHeurSol("/home/tsauter/GraphILP/GraphILP-API/graphilp/examples/setcoverTestInstances/scpd1.txt")
# -


