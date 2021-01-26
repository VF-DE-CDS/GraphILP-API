# Importing needed Libraries and ILPGraph to store the information in
from gurobipy import *
import networkx as nx
import re
from .ilpgraph import ILPGraph


# +
# Doing the conversion and Import of a STP Files
def read(G):
    
    result = ILPGraph()
    result.setNXGraph(G)
    
    return result

def stp_to_networkx(path):
    """
    Creates a networkx object given a path to a .stp file.
    A .stp file contains edges and nodes. The first line depicts the starting node. 
    Each line starting with an "E" is followed by both edge's points and it's distance(?).
    Each line starting with a "T" is followed by a Terminal.
    
    :param path: path to .stp file
    :type path: str
    :rtype: networkx undirected graph
    """
    
    path = "/mnt/data/projects/ILP/steiner/PUC/bip42u.stp"
    with open(path, "rt") as input_file:
        lines = input_file.readlines()
    terminals = []
    edges = []
    
    for line in lines:
        # Remove + characters. This is not always necessary
        line = re.sub(' +', ' ', line)
        # Found a new Edge
        if line.startswith('E '):
            # Extracting information(startingNode endingNode Distance)
            parts = line.rstrip().split(" ")[1:]
            
            # Parse the data into tuples and from Array of Integer and append to list of all edges
            tuple_data = tuple(int(p) for p in parts)
            edges.append((tuple_data[0], tuple_data[1], {'weight':tuple_data[2]}))

        # Found a Terminal Node
        if line.startswith('T '):
            terminals.append(int(line.rstrip().split(" ")[1]))
        
    # Create a new NetworkX Object, i.e. Graph
    G = nx.Graph()

    # Fill the Graph with our edges. This method automatically fills in the Nodes as well.
    G.add_edges_from(edges)

    return G, terminals

# -


