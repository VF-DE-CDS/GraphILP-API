# +
import sys, os
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../../..'))
import numpy as np
import scipy.sparse as sp
from imports import ilpsetsystem as ilpss
from imports import readFile
import graphilp.covering.heuristics.coverHelpers as covHelp



def getHeurSol(coverMatrix, k, sets, numNodes, weightUniverse = None):
    """
        Returns the Heuristic Solution calculated by a greedy approximation algorithm for the k - coverage Problem.
        The k - coverage problem greedily finds the maximum amount of Nodes we can cover with k sets.
        
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
    chosenNodes = set()
    numSets = len(sets)
    universe = set(i for i in range(numNodes))
    

    containingSets, containedNodes, setSizes = covHelp.extract(coverMatrix, numSets)


    # Iterate over the whole universe, i.e. the nodes in the model
    while universe != chosenNodes:
        chosenSets, chosenNodes = covHelp.getNextSet(chosenSets, chosenNodes, sets, numNodes, setSizes, containedNodes)
        
        # Break if the maximum amount of sets allowed to be chosen is reached.
        if (k <= len(chosenSets)):
            break
    return chosenSets, chosenNodes
