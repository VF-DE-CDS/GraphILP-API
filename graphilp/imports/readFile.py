# + endofcell="--"
import sys
sys.path.append("../..")
from graphilp.imports import ilpgraph
import networkx as nx
import re
from scipy.sparse import csc_matrix
import numpy as np


# # +
# Doing the conversion and Import of a STP Files
def read(G):

    result = ILPGraph()
    result.setNXGraph(G)

    return result

def edges_to_networkx(path):
    """
    Creates a networkx object given a path to an .edges file.
    A .edges file contains edges. Nodes are later on extracted by NetworkX
    
    :param path: path to .edges file
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
        # Extracting information(startingNode endingNode Distance)
        parts = line.rstrip().split(" ")

        # Parse the data into tuples and from Array of Integer and append to list of all edges
        tuple_data = tuple(int(p) for p in parts[:2])
        edges.append((tuple_data[0], tuple_data[1]))
    # Create a new NetworkX Object, i.e. Graph
    G = nx.Graph()

    # Fill the Graph with our edges. This method automatically fills in the Nodes as well.
    G.add_edges_from(edges)
    return G


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

    # Create a new NetworkX Object, i.e. Graph
    G = nx.Graph()

    # Fill the Graph with our edges. This method automatically fills in the Nodes as well.
    G.add_edges_from(edges)

    return G, terminals

def mis_to_networkx(path):
    """
    Creates a networkx object given a path to a .mis file.
    A .stp file contains edges and nodes. The first line depicts the starting node. 
    Each line starting with an "e" is followed by both edge's points.
    
    :param path: path to .mis file
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
    
def read_tsplib(file_name):
    """
    This function parses an XML file defining a TSP (from TSPLIB
    http://www.iwr.uni-heidelberg.de/groups/comopt/software/TSPLIB95/)
    and returns the Adjacency Matrix that cna be then used to construct a PyGMO.problem.tsp
    Args:
            file_name (string): The XML file to be opened for parsing.
    Returns:
            adj_mat (double): Adjacency Matrix, 0 per diagonal.
    Raises:
    IOError:
            The input file was not found.
    TypeError:
            At least one of the attributes in an edge
            of the XML file is missing or of the wrong type.
    xml.etree.ElementTreeParseError:
            There was an error parsing the file.
            See: https://docs.python.org/2.7/library/xml.etree.elementtree.html
    """
    import xml.etree.ElementTree as ET
    try:
        tree = ET.parse(file_name)
    except ET.ParseError as e:
        print('There was a problem parsing', fileName, ':\n', e)
        return
    except IOError as e:
        print('There was a problem opening the file:\n', e)
        return

    # get root
    root = tree.getroot()

    # graph data (list of list: [[]])
    adj_mat = []
    symmetric = False
    try:  # in case vertex.cost attribute is not set or incorrect type
        for idx_from, vertice in enumerate(root.iter('vertex')):
            tmp = []
            for idx_to, edge in enumerate(vertice):
                # symmetric problems don't have values for main diagonal
                if idx_from == idx_to != int(edge.text):  # insert diagonal 0's
                    tmp.append(0)
                    symmetric = True
                tmp.append(float(edge.get('cost')))
            adj_mat.append(tmp)
        if symmetric:
            adj_mat[idx_to + 1].append(0)  # set last diagonal element to 0
    except TypeError:
        print('One of the values of the graph attributes is not valid.')
        print('Hint:', idx_from, '->', idx_to, '=', edge.get('cost'))
        return

    return adj_mat


def _symmetric_tril(mat):
    """
    If a matrix is symmetric, returns a copy with elements above the main diagonal zeroed.
    Args:
            mat ([[]]]): A square matrix.
    Returns:
    tril ([[]]): The matrix with only lower diagonal items.
    """
    import numpy
    mat = numpy.array(mat)

    if (mat.transpose() == mat).all():
        mat = numpy.tril(mat)

    return mat.tolist()


def _print_matrix(mat, show_all=False):
    import numpy
    numpy.set_printoptions(linewidth=100)
    numpy.set_printoptions(precision=3)
    # this forces to print all elements on a long row, on the next line
    # otherwise, center elements are snipped '...,' to fit line of 100
    if show_all:
        numpy.set_printoptions(threshold='nan')

    print(numpy.array(mat))
    
def read_set_cover(path):
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
        
    return sparseMatrix
        
# -
# --




