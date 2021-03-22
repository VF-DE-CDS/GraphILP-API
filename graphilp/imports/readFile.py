# + endofcell="--"
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

def read_tsplib(file_name):
    """
    This function parses an XML file defining a TSP (from TSPLIB
    http://www.iwr.uni-heidelberg.de/groups/comopt/software/TSPLIB95/)
    and returns the Adjacency Matrix that can be then used to construct a PyGMO.problem.tsp
    
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

    return sparseMatrix, sets
        
# -
# --
