# +
from graphilp.imports import ilpgraph
import sys
sys.path.append("..")
from imports import ilpgraph
import networkx as nx
import re
from scipy.sparse import csc_matrix
import numpy as np

def edges_to_networkx(path):
    """
    Creates a NetworkX Graph from an .edges file (`Network Repository format <http://networkrepository.com>`__).
    
    Network Repository is a large collection of network graph data for research and benchmarking.
    
    :param path: path to .edges file
    :type path: str
    :returns: a `NetworkX Graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    """

    with open(path, "rt") as input_file:
        lines = input_file.readlines()
    edges = []


    for line in lines:
        # Remove + characters. This is not always necessary
        line = re.sub(' +', ' ', line)
        # Found a new Edge
        # Extracting information(startingNode endingNode Distance)
        parts = line.rstrip().split(" ")

        # Parse the data into tuples and from Array of Integer and append to list of all edges
        tuple_data = tuple(int(p) for p in parts[:2])
        edges.append((tuple_data[0], tuple_data[1]))
        
    # Create a new NetworkX Graph object
    G = nx.Graph()

    # Fill the graph with our edges. This method automatically fills in the nodes as well.
    G.add_edges_from(edges)
    
    return G


def stp_to_networkx(path):
    """
    Creates a NetworkX Graph from an .stp file (`SteinLib format <http://steinlib.zib.de/format.php>`__).
    
    `SteinLib <http://steinlib.zib.de/steinlib.php>`__ is a collection of Steiner tree 
    problems in graphs and variants.
    
    The format description can be found `here <http://steinlib.zib.de/format.php>`__ on the SteinLib pages.
    
    :param path: path to .stp file
    :type path: str
    :returns: a `NetworkX Graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
        and a list of terminals
    
    Example:
        G, terminals = stp_to_networkx("steinlib_instance.stp")
    """

    with open(path, "rt") as input_file:
        lines = input_file.readlines()
        
    edges = []
    terminals = []

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

    # Create a new NetworkX Graph object
    G = nx.Graph()

    # Fill the graph with our edges. This method automatically fills in the nodes as well.
    G.add_edges_from(edges)

    return G, terminals

def mis_to_networkx(path):
    """
    Creates a NetworkX Graph from a .mis file (ASCII DIMACS graph format).
    
    This is used for maximum independet set benchmarking data 
    from `BHOSLIB <http://sites.nlsde.buaa.edu.cn/~kexu/benchmarks/graph-benchmarks.htm>`__.
    
    :param path: path to .edges file
    :type path: str
    :returns: a `NetworkX Graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
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

    # Create a new NetworkX Graph object
    G = nx.Graph()
    
    # Fill the graph with our edges. This method automatically fills in the nodes as well.
    G.add_edges_from(edges)

    return G

def col_file_to_networkx(path):
    """
    Creates a networkx object given a path to a .col file.
    A .col file only contains edges. Each line starting with an "e" is followed by both edge's points.
    
    :param path: path to .col file
    :type path: str
    :rtype: networkx undirected graph
    """
    
    edges_list = []
    
    with open(path) as f:
        for line in f.readlines():
            if line.startswith('e'):
                line = line.replace('/n', '')
                line_splitted = line.split()
                edge = (line_splitted[1], line_splitted[2])
                edges_list.append(edge)
    
    G = nx.Graph()
    G.add_edges_from(edges_list)
    return G
    
def read_set_cover(path):
    """ TODO
    
    :param path: path to ??? file
    
    :returns: sparse matrix and sets
    """
    sets = dict()
    curSet = 0
    curRow = 0
    readElements = 0
    curRowLength = 0
    
    with open(path, "rt") as input_file:
        lines = input_file.readlines()
    
    line = lines[0].split(" ")
    numNodes = int(line[1])
    numSets = int(line[2])
    sparseMatrix = csc_matrix((numNodes, numSets), dtype = np.int8).toarray()
    lines.pop(0)

    for line in lines:
        # Split After Spaces
        curLine = line.split(" ")
        if curSet < numSets:
            for element in curLine:
                if element != '' and element != '\n':
                    sets[curSet] = dict(weight = int(element))
                    curSet += 1
            continue
        # Arrived at the other section, we got a new column now, gotta skip this line
        else:
            if (curRow == 0 and curRowLength == 0):
                curRowLength = int(curLine[1])
            if readElements >= curRowLength:
                curRow += 1
                curRowLength = int(curLine[1])
                readElements = 0
            else:
                for element in curLine:
                    if element != '' and element != '\n':
                        sparseMatrix[curRow][int(element) - 1] = 1
                        readElements += 1

    return sparseMatrix, sets
