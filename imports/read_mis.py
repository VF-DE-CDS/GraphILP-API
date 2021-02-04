import sys, os
sys.path.append(os.getcwd())
sys.path.append(os.path.abspath('..'))
from imports import ilpgraph
from imports import networkx as imp_nx
from covering import min_vertexcover as minVC
import networkx as nx
from gurobipy import *
import xlsxwriter


# +
# Doing the conversion and Import of a STP Files
def read(G):
    
    result = ILPGraph()
    result.setNXGraph(G)
    
    return result

def mis_to_networkx(path):
    """
    Creates a networkx object given a path to a .stp file.
    A .stp file contains edges and nodes. The first line depicts the starting node. 
    Each line starting with an "E" is followed by both edge's points and it's distance(?).
    Each line starting with a "T" is followed by a Terminal.
    
    :param path: path to .stp file
    :type path: str
    :rtype: networkx undirected graph
    """
    
    with open(path, "rt") as input_file:
        lines = input_file.readlines()
    edges = []
    
    for line in lines:
        # Remove + characters. This is not always necessary
        line = re.sub(' +', ' ', line)
        # Found a new Edge
        if line.startswith('e '):
            # Extracting information(startingNode endingNode Distance)
            parts = line.rstrip().split(" ")[1:]
            
            # Parse the data into tuples and from Array of Integer and append to list of all edges
            tuple_data = tuple(int(p) for p in parts)
            edges.append((tuple_data[0], tuple_data[1]))
        
    # Create a new NetworkX Object, i.e. Graph
    G = nx.Graph()
    # Fill the Graph with our edges. This method automatically fills in the Nodes as well.
    G.add_edges_from(edges)

    return G

# -


