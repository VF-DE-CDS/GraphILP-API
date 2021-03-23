# +
import sys, os
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../../..'))
sys.path.append(os.path.abspath('.'))
import numpy as np
import scipy.sparse as sp
from imports import ilpsetsystem as ilpss
from graphilp.covering.heuristics import coverHelpers as covHelp

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
    chosenNodes = set()
    numSets = len(sets)
    universe = set(i for i in range(numNodes))
    

    containingSets, containedNodes, setSizes = covHelp.extract(coverMatrix, numSets)

    while universe != chosenNodes:
        costEff = covHelp.calculateSetEfficiencies(numNodes, chosenNodes, setSizes, sets)
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


