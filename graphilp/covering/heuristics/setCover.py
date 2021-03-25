# +
import sys, os
sys.path.append(os.path.abspath('../..'))
import numpy as np
import scipy.sparse as sp
from imports import ilpsetsystem as ilpss
from . import coverHelpers as covHelp

def getHeurSol(coverMatrix, sets, universe, k = None):
    """
        Returns the Heuristic Solution calculated by a greedy approximation algorithm for the SetCoverage Problem.
        If paramter k is specified, the Problem turns into a k - coverage problem. A k - coverage Problem Heuristic 
        greedily finds the maximum amount of Nodes we can cover with k sets.
        
        :param coverMatrix: Cover Matrix defining which Node is contained in which set
        :param k: Maximum Sets to use
        :param sets: Sets that cover Nodes
        :params universe: List of Weighted Nodes that are to be covered
        :type coverMatrix: List of List
        :type k: int, optional
        :type sets: Dict of int:dict pairs. The value needs to specifiy a weight.
        :type universe: list of int
        :return: A list of the Sets covering the chosen Nodes, A list of Nodes contained in the solution
        :rtype: list of int, list of int
    """
    
    chosenSets = []
    costEfficiencies = dict()
    chosenNodes = set()
    numSets = len(sets)
    numNodes = len(universe)
    
    # Extract the essential information we need from the Cover Matrix
    containingSets, containedNodes, setSizes = covHelp.extract(coverMatrix, numSets)
    
    # If no k is specified, we are handling a set covering problem
    if k == None:
        k = numNodes
        
    # Greedily choose sets to include in the solution either until all Nodes are covered or until the maximum amount of Sets
    # used to cover are reached
    while universe != chosenNodes and k > len(chosenSets):
        chosenSets, chosenNodes = covHelp.getNextSet(chosenSets, chosenNodes, sets, numNodes, setSizes, containedNodes)
    
    return chosenSets, chosenNodes

# -


