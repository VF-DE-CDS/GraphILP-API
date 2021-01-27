import sys
sys.path.append("..")
from imports import ilpgraph, graph_parser
from imports import networkx as imp_nx
import networkx as nx 

def maximalMatching(G):
    """
    Implements the maximal matching heuristic in order the create an initial heuristic solution 
    for the optimzation process to take shorter.

    :param G: A Graph consisting of Edges and Nodes
    :type G: NetworkX Graph
    """

    edges = list(G.edges())
    nodes = list(G.nodes())
    chosenEdges = []

    while len(edges) != 0:
        edgesCopy = list.copy(edges)

        edge = edges[0]
        startNode = edges[0][0]
        endNode = edges[0][1]

        chosenEdges.append(edge)
        edgesCopy.remove(edge)
        edges.remove(edge)
        for i in range(len(edgesCopy)):

            curEdgeStart = edgesCopy[i][0]
            curEdgeEnd = edgesCopy[i][1]

            if (curEdgeStart == startNode or curEdgeEnd == startNode or curEdgeStart == endNode or curEdgeEnd == endNode):
                edges.remove(edgesCopy[i])

    print(chosenEdges)

if __name__ == '__main__':
    G = imp_nx.col_file_to_networkx('')
    maximalMatching(G)