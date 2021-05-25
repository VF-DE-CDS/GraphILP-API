import pickle
import networkx as nx
import pandas as pd
import pcst_fast
import matplotlib.pyplot as plt


def createDataframes(G):
    # EDGES: Transforming Edges to Dataframe
    edgesList = list(G.edges())
    costs = []

    # NODES: Transform Nodes to DataFrame
    nodesList = list(G.nodes())
    prices = []

    # EDGES: Extracting the Costs from the 'Attributes' - Dictionary returned by G.edges(data=True)
    for row in G.edges(data=True):
        costs.append(row[2]['weight'])

    # NODES: Extracting the prices of the Nodes from the 'Attributes' - Dictionary returned by G.nodes(data=True)
    for row in G.nodes(data=True):
        prices.append(row[1]['prize'])

    # EDGES: Creating a list of tuples. Each element is built up the structure 'startNode, endNode, costOfEdge'
    edges = []
    for i in range(len(costs)):
        edges.append((edgesList[i][0], edgesList[i][1], costs[i]))

    # NODES: Creating a list of tuples. Each element is built in the structure 'NewNodeIndex, Node, PriceOfNode'
    nodes = []
    for i in range(len(prices)):
        nodes.append((i, nodesList[i], prices[i]))

    # EDGES: Create DataFrame from the Edges List
    dfEdges = pd.DataFrame(edges, columns=['Node 1', 'Node 2', 'Costs'])

    # NODES: Create DataFrame from the Nodes List
    dfNodes = pd.DataFrame(nodes, columns=['NewNodeIndex', 'Node', 'prize'])
    # ** END MANIPULATION

    return dfNodes, dfEdges


def findIndeces(dfNodes, terminals=None, root=None, accesspoints=None):
    # Find the index of the artificial Root in the DataFrame
    # dfNodes.query is a Pandas Dataframe method
    # @root is used to specify we are searching for the variable root
    # iloc gets the value at the [nth] position
    # 'NewNodeInde' is the value we are finally interested in
    if root != -1:
        rootIndex = int(dfNodes.query('Node == @root').iloc[0]['NewNodeIndex'])
    else:
        rootIndex = -1

    # Find the indeces of the Terminals in the Dataframe. Same as with the root
    listTerminalsIndeces = dfNodes.query('Node == @terminals').values.tolist()
    terminalsIndeces = []
    for entry in listTerminalsIndeces:
        terminalsIndeces.append(entry[0])

    listAccesspointsIndeces = dfNodes.query('Node == @accesspoints').values.tolist()
    accesspointsIndeces = []
    for entry in listAccesspointsIndeces:
        accesspointsIndeces.append(entry[0])

    return rootIndex, terminalsIndeces, accesspointsIndeces


def mergeDataFrames(dfNodes, dfEdges):
    # The Final Dataframe contains all information needed for the transformation both into the new Data format and
    # from the new Data format.
    # It is important not to change dfFinal!
    # The label on the columns is arbitrary.
    # NewNodeIndex_Node1 and NewNodeIndex_Node2 refers to the new labels of the nodes
    dfFinal = dfEdges.merge(dfNodes, left_on='Node 1', right_on='Node')
    dfFinal = dfFinal.merge(dfNodes, left_on='Node 2', right_on='Node', suffixes=('_Node1', '_Node2'))

    # Since we don't want to change the dfFinal, we make a copy to continue our work
    dfChanged = dfFinal.copy()

    # First, we change the labels of the start and end nodes of the edges to the new format.
    # Since we already have the new format in the dfFinal and dfChanged, all we have to do is to assign new values
    # to the respecte Node 1 and Node 2 Columns.
    dfChanged['Node 1'] = dfChanged['NewNodeIndex_Node1']
    dfChanged['Node 2'] = dfChanged['NewNodeIndex_Node2']

    # Then we can drop the columns containg the old labels as to have a more condensed dataFrame
    # dfChanged is now built up in the following structure:
    # StartNode, EndNode, CostOfEdge, PriceStartNode, PriceEndNode
    dfChanged = dfChanged.drop(columns=['Node_Node1', 'Node_Node2', 'NewNodeIndex_Node1', 'NewNodeIndex_Node2'])

    return dfFinal, dfChanged


def dataframeToList(dfFinal, dfNodes, dfChanged):
    # All the information we need is stored in the dataframe. Now we need to exract the information and put it
    # into the right format for the pcst_fast library, i.e. lists where the position in the array defines
    # the attributes of nodes / edges

    # First, we extract the edges, i.e. StartNode and EndNode
    edges = dfChanged[['Node 1', 'Node 2']].values.tolist()

    # Next, we can extract the Prices of the Nodes and the Costs of the Edges and also put those into a list.
    nodePrices = dfNodes['prize'].values.tolist()
    edgeCosts = dfFinal['Costs'].values.tolist()

    return edges, nodePrices, edgeCosts


def extractSolution(result_nodes, terminalsIndeces, accesspointsIndeces):
    containedTerminals = []
    containedAccesspoints = []
    contained = False
    for node in result_nodes:
        if node in terminalsIndeces:
            containedTerminals.append(node)
        if node in accesspointsIndeces:
            containedAccesspoints.append(dfNodes.iloc[node]['Node'])
    if containedTerminals == terminalsIndeces:
        contained = True

    #print("All Terminals contained in the solution: ", contained)
    #print("Contained Accesspoints: ", containedAccesspoints)

    return containedTerminals, containedAccesspoints


def reformatToGraph(result_nodes, result_edges, dfFinal, dfNodes):
    resultingEdges = dfFinal.iloc[result_edges]
    resultingEdges = resultingEdges[['Node 1', 'Node 2', 'Costs']]
    #resultingGraph = nx.from_pandas_dataframe(resultingEdges, 'Node 1', 'Node 2', 'Costs')
    resultingGraph = nx.from_pandas_edgelist(resultingEdges, 'Node 1', "Node 2", edge_attr='Costs')

    resultingNodes = dfNodes.iloc[result_nodes]
    resultingNodes = resultingNodes.drop(columns=['NewNodeIndex'])
    prizesList = resultingNodes.to_dict('split')['data']
    for i in range(len(prizesList)):
        resultingGraph.nodes[prizesList[i][0]]['prize'] = prizesList[i][1]

    return resultingNodes, resultingEdges, resultingGraph, prizesList


def format(G, terminals=None, root=None, accesspoints=None):
    return resultingGraph


def instantiateManualGraph():
    G = nx.Graph()

    G.add_nodes_from([
        (1, {'prize': 0}),
        (2, {'prize': 0}),
        (3, {'prize': 0}),
        (4, {'prize': 0}),
        (5, {'prize': 0}),
        (6, {'prize': 0}),
        (7, {'prize': 20}),
        (8, {'prize': 0}),
        (9, {'prize': 0})
    ])

    G.add_edges_from([(1, 2, {'weight': 3}), (1, 5, {'weight': 4}), (2, 3, {'weight': 1}),
                               (2, 4, {'weight': 1}), (3, 4, {'weight': 1}), (5, 6, {'weight': 2}),
                               (5, 7, {'weight': 1}), (6, 4, {'weight': 7}), (7, 8, {'weight': 2}), (8, 4, {'weight': 3}), (7, 9, {'weight': 2})])
    terminals = [1,4,7,9]
    artificialRoot = 3
    return G, terminals, artificialRoot


def defineTerminalPrices(G, TerminalsPrice):
    for i in G.nodes():

        # If a terminal was found, set it's price to be the TerminalsPrice variable
        if (i in terminals):
            G.nodes[i]['prize'] = TerminalsPrice

        # Else the prize is 0 (Steiner node)
        else:
            G.nodes[i]['prize'] = 0
    return G


if __name__ == '__main__':
    anaGraph = False
    printResultingGraph = False
    printNodesAndEdges = True

    # Randomly chosen Nodes for an artificial root which is then only connected to the accesspoints
    artificialRoot = (3784533.0, 5545823.0)

    # Fixed price which is the same for all Terminals
    TerminalsPrice = 60000

    # Fixed cost which is the same for all the artificial edges going from the artificial Root to the
    # Accesspoints
    artificialEdgeCost = 0

    # Creating a Test Instance for a Graph with Edges, Edge weights, Nodes and Prices on the Nodes
    # This is the same format the input files from Ana are using
    if (anaGraph == False):
        G, terminals, artificialRoot = instantiateManualGraph()

    else:
        with open('accesspoints', 'rb') as f:
            accesspoints = pickle.load(f)

        with open('terminals', 'rb') as f:
            terminals = pickle.load(f)

        with open('graph', 'rb') as f:
            G = pickle.load(f)

        artificialEdges = []
        # Create edges from the artifical root to all the accesspoints (APs)
        for ap in accesspoints:
            artificialEdges.append((artificialRoot, ap, {'weight': artificialEdgeCost}))

        # Add the artificial Edges from the artificial Root to the AP to the Graph
        G.add_edges_from(artificialEdges)

    #G = defineTerminalPrices(G, TerminalsPrice)
    dfNodes, dfEdges = createDataframes(G)
    rootIndex, terminalsIndeces, accesspointsIndeces = findIndeces(dfNodes, terminals, artificialRoot)  # accesspoints)
    dfFinal, dfChanged = mergeDataFrames(dfNodes, dfEdges)
    edges, nodePrices, edgeCosts = dataframeToList(dfFinal, dfNodes)

    # Let PCST_fast do its magic, i.e. optimizing the problem setting
    result_nodes, result_edges = pcst_fast.pcst_fast(edges, nodePrices, edgeCosts, rootIndex, 1, 'strong', 0)

    containedTerminals, containedAccesspoints = extractSolution(result_nodes)
    resultingNodes, resultingEdges, newGraph, prizesList = reformatToGraph(result_nodes, result_edges, dfFinal)

    if (printNodesAndEdges):
        print("Chosen nodes by pcst_fast: \n", resultingNodes)
        print("Chosen edges by pcst_fast: \n", resultingEdges)

    if (printResultingGraph):
        labels = nx.get_edge_attributes(newGraph, 'Costs')
        pos = nx.spring_layout(newGraph)
        nx.draw_networkx_nodes(G, pos)
        nx.draw_networkx_edges(G, pos)
        print(labels)
        nx.draw(newGraph, with_labels=True, font_weight='bold')
        nx.draw_networkx_edge_labels(G, labels, font_size=8)
        plt.show()
