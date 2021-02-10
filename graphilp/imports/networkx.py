import networkx as nx
from .ilpgraph import ILPGraph

# +
def read(G):
    
    result = ILPGraph()
    result.setNXGraph(G)
    
    return result

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
    