# +
import numpy as np

def extract(coverMatrix, numSets):
    """
    Extracts the information from the cover Matrix.
    I.e. which node is stored in which set and which set contains which node.
    Also extracts the size of each set.
    
    :param coverMatrix: Cover Matrix defining which Node is contained in which set 
    :param numSets: Total amount of Sets
    :type coverMatrix: list of list of int
    :type numSets: int
    :return: sets containing each node, nodes contained in each set, amount of Nodes contained in each set 
    :rtype: list of lists of int, list of lists of int, list of int
    """
    containingSets = dict()
    containedNodes = dict()
    setSizes = np.zeros(numSets)
    for i in range(len(coverMatrix)):
        # Set of the Nodes that are contained in the current solution.
        containingSets[i] = set()

        # Iterate through every set and check whether the current node i is contained in this set
        for j in range (len(coverMatrix[i])):

            # For the very first node, we have to instantiate the array
            if (i == 0):
                containedNodes[j] = set()

            # Fill two arrays with information
            if coverMatrix[i][j] > 0:
                # First fill the array which gives information about which set contains the current node
                containingSets[i].add(j)
                # Count the size of the set, i.e. how many nodes this set containts (i.e. the cardinality of the set)
                setSizes[j] += 1
                # Second fill the array which gives information about which nodes the current set contains
                containedNodes[j].add(i)

    setSizes = setSizes.tolist()
    return containingSets, containedNodes, setSizes 


# Calculate the "Efficiency" of each set. The efficiency is defined by the average weight of each node in a set divided
# by the amount of the nodes that are not yet in the solution.
def calculateSetEfficiencies(numNodes, chosenNodes, setSizes, sets):
    costEfficiencies = dict()
    cardinNotChosen = numNodes - len(chosenNodes)
    for i in range(len(sets)):
        costEfficiencies[i] = (sets[i]['weight'] / setSizes[i]) / cardinNotChosen
    return costEfficiencies

def getNextSet(chosenSets, chosenNodes, sets, numNodes, setSizes, containedNodes):
    # Get the update Cost Efficiency for every Set
    costEff = calculateSetEfficiencies(numNodes, chosenNodes, setSizes, sets)
    
    # If the set has already been chosen, artificially set the efficiency of this set very high
    # This way this set won't be chosen again, since the lower the efficiency, the better
    for i in range(len(sets)):
        if i in chosenSets:
            costEff[i] = 10000
    # Find the set with the minimum cost Efficiency
    minSet = min(costEff.keys(), key=(lambda k: costEff[k]))
    # All the nodes from the set with the set with the least efficiency are added to the solution.
    chosenNodes = containedNodes[minSet].union(chosenNodes)
    # The chosen set must not be chosen again
    chosenSets.append(minSet)
    return chosenSets, chosenNodes    
