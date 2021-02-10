import gurobipy as gp
import networkx as nx

def createWarmstart(G, m, node_to_color=None):
    """
    Sets a warmstart solution on given Gurobi-model m and ILPGraph G. If node_to_color is None, the greedy coloring algorithm is run to obtain an initial solution.
    
    :param G: Graph corresponding to Gurobi model
    :type G: ILPGraph
    :param m: Model to set warmstart for
    :type m: Gurobi model
    :param node_to_color: (optional) Solution to the coloring problem in form of a dictionary: {node_1:color_of_node_1, ...}
    :type node_to_color: dict
    
    """
    
    if node_to_color is None:
    #obtain greedy solution for warmstart
        color_to_node, node_to_color = greedyColoring(G)
    
    #set every node-color-assignment-variable to zero
    for assign_var in G.node_assignment_variables:
        G.node_assignment_variables[assign_var].start = 0.0
    m.update()
    
    #set assignment obtained as given by node_to_color
    for node, col in node_to_color.items():
        G.node_assignment_variables[node,col].start = 1.0
    m.update()


def createModel(G, **kwargs):
    r""" 
    Create an ILP for minimum vertex coloring.
    
    :param G: graph to find minimum vertex coloring for
    :type G: ILPGraph
    :rtype: Gurobi model
    
    ILP:    
        .. math::
            :nowrap:
            
            \begin{align*}
            \min \sum_{1\le i \le H}w_{i} && \text{ (minimize the total number of colors used) }\\
            \text{s.t.} \\
            \sum_{i=1}^{H} x_{vi} = 1\;\forall v\in V && \text{ (make sure every vertex gets exactly one color) } \\
            x_{ui}+x_{vi}\le w_{i}\;\forall(u,v)\in E, i=1,\ldots,H && \text{ (make sure no two neighboring vertices get the same color) } \\
            x_{vi},w_{i}\in\{0,1\}\;\forall v\in V, i=1,\ldots, H && \text{ (assigning a color or not is a binary decision) }
            \end{align*}
    """
    
    #initialize gurobi model
    m = gp.Model('graphilp_min_vertex_coloring')
    
    if not hasattr(G, 'G_integer_labeled'):
        G.G_integer_labeled = nx.convert_node_labels_to_integers(G.G,
                                                               first_label=0)
    nodes = G.G_integer_labeled.nodes()
    edges = G.G_integer_labeled.edges()
    
    #add decision variables
    max_number_colors = __get_max_number_colors__(G)
    color_used_vars = m.addVars(max_number_colors, name='color_used', vtype=gp.GRB.BINARY)
    #whether or not each vertex is assigned to color c
    node_color_vars = m.addVars(nodes, max_number_colors, name='color_assignment', vtype=gp.GRB.BINARY)
    #G.setNodeAssignmentVars(node_color_vars)
    G.node_assignment_variables = node_color_vars
    
    m.update()
    
    #objective is to minimize the number of colors used
    m.setObjective(gp.quicksum(color_used_vars), gp.GRB.MINIMIZE)
    
    #add constraints (problem: this assumes nodes and edges in graph object correspond to index based variables as added above -> could be solved via ILPGraph?)
    
    #for each node: exactly one color must be assigned
    for node in nodes:
        m.addConstr(node_color_vars.sum(node, '*')==1)
    
    #two neighboring nodes can not have the same color assigned
    for edge in edges:
        m.addConstrs(node_color_vars[edge[0],color]+node_color_vars[edge[1],color]<=color_used_vars[color] for color in color_used_vars)

    #strengthen formulation
    for i in range(1, len(color_used_vars)):
        m.addConstr(color_used_vars[i]<=color_used_vars[i-1]) #only assign color i if color i-1 is assigned already
    
    m.update()
    return m

def extractSolution(G, model):
    """
    Get a dictionary with colors as keys and a list of nodes with that color assigned as values.
    
    :param G: graph to find minimum vertex coloring for
    :type G: ILPGraph
    :param model: ILP solved for minimum vertex coloring
    :type model: Gurobi model
    :rtype: dictionary
    """
    
    col_to_node = {}
    node_to_col = {}
    
    for var, sol_var in G.node_assignment_variables.items():
        if sol_var.X>0.5:
            color = var[1]
            node = var[0]
            node_to_col[node] = color
            if not color in col_to_node.keys():
                col_to_node[color] = [node]
            else:
                col_to_node.get(color).append(node)
            
    return col_to_node, node_to_col


def __get_max_number_colors__(G, method='greedy'):
    """
    Helper function to get an upper bound for the number of colors to be used. If method=='greedy': Returns number of nodes required by greedy algorithm. Else: Returns number nodes in G.
    
    :param G: Graph
    :type G: ILPGraph
    :rtype: int
    """
    if method=='greedy':
        greedy_col_to_node, greedy_node_to_col = greedyColoring(G)
        return len(greedy_col_to_node.keys())
    
    return G.G.number_of_nodes()

def colors_list_from_assignment_dict(G, color_assignment):
    """
    Helper function to create a list of colors from a color_assignment dictionary as returned by extractSolution()
    
    :param G: Graph corresponding to color_assignment
    :type G: ILPGraph
    :param color_assignment: solution to minimum vertex cover problem as returned by extractSolution
    :type color_assignment: dict
    :rtype: list
    """
    colors = [-1]*G.G.number_of_nodes()

    for color, assigned_nodes in color_assignment.items():
        for node in assigned_nodes:
            colors[node] = color
    return colors


# +
def _first_available(color_list):
    """
    (https://en.wikipedia.org/wiki/Greedy_coloring)
    Return smallest non-negative integer not in the given list of colors.
    
    :param color_list: List of neighboring nodes colors
    :type color_list: list of int
    :rtype: int
    """
    color_set = set(color_list)
    count = 0
    while True:
        if count not in color_set:
            return count
        count += 1

def greedyColoring(G):
    """
    Applies the greedy coloring algorithm (explanation and code: https://en.wikipedia.org/wiki/Greedy_coloring) and returns two dictionaries: {color_1:[list_of_color_1_nodes], ...} and {node_1:color_of_node_1, ...}
    
    :param G: Graph to apply greedy coloring algorithm to
    :type G: ILPGraph
    :rtype: 2-tuple of dicts
    """
    
    if not hasattr(G, 'G_integer_labeled'):
        G.G_integer_labeled = nx.convert_node_labels_to_integers(G.G,
                                                               first_label=0)
    nodes = G.G_integer_labeled.nodes()
    
    node_to_col = {}
    col_to_node = {}
    
    for node in nodes:
        neighbor_colors = [node_to_col.get(neigh_node) for neigh_node in G.G_integer_labeled.neighbors(node)]
        node_color = _first_available(neighbor_colors)
        node_to_col[node] = node_color
        if not node_color in col_to_node.keys():
            col_to_node[node_color] = [node]
        else:
            col_to_node.get(node_color).append(node)
    
    return col_to_node, node_to_col
# -


