# +
#import numpy as np
#import scipy.sparse as sp
#from imports import ilpsetsystem as ilpss
#from imports import readFile
#import time
#from covering.heuristics import coverHelpers as covHelp

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

def getHeuristic(coverMatrix, sets, universe):
    """
        Returns the Heuristic Solution calculated by a greedy approximation algorithm for the set Packing Problem.
        
        :param coverMatrix: Cover Matrix defining which Node is contained in which set
        :param sets: Sets that cover Nodes
        :param universe: List of Nodes that are to be covered
        :type coverMatrix: List of List
        :type k: int, optional
        :type sets: Dict of int:dict pairs. The value needs to specifiy a weight.
        :type universe: list of int
        :return: A list of the Sets covering the chosen Nodes
        :rtype: list of int, list of int
    """
    # Instantiation of the Datastructures
    chosenSets = []
    chosenNodes = set()
    numSets = len(sets)
    setSizes = np.zeros(numSets)
    numNodes = len(universe)

    # Extract the essential information we need from the Cover Matrix
    containingSets, containedNodes, setSizes = covHelp.extract(coverMatrix, numSets)

    while sets != {}:
        # costEfficiencies define how good picking each set is for us
        costEff = calculateSetEfficiencies(chosenSets, setSizes, sets)
        # The minimum efficiency is the best set we can pick (greedy)
        minSet = min(costEff.keys(), key=(lambda k: costEff[k]))
        # Unify the added Nodes with the ones already existing in the solution
        chosenNodes = containedNodes[minSet].union(chosenNodes)
        
        chosenSets.append(minSet)
        sets = removeSets(sets, chosenNodes, containedNodes)
        
    return chosenSets, chosenNodes
