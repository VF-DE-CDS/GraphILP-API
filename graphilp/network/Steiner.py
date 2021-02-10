# +
from gurobipy import *
import networkx as nx

# a dictionary translating edge variables to edge names for the callback
var2edge = None

# a dictionary translating edge names to edge variables for the callback
edge2var = None

def createModel(G, terminals, weight='weight', cycleBasis: bool = False, nodeColoring: bool = False):    
    r""" Create an ILP for the minimum Steiner tree problem in graphs.

    Some more text.
    
    :param G: an ILPGraph
    :param terminals: a list of nodes that need to be connected by the Steiner tree
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost

    :return: a Gurobi model
        
    ILP:
        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{(i,j) \in E} w_{ij} x_{ij}\\
            \text{s.t.} &&\\
            x_{ij} + x_{ji} \leq 1 && \text{(restrict edges to one direction)}\\
            x_r = 1 && \text{(require root to be chosen)}\\
            \sum x_i - \sum x_{ij} = 1 && \text{(enforce circle when graph is not connected)}\\
            2(x_{ij}+x_{ji}) - x_i - x_j \leq 0 && \text{(require nodes to be chosen when edge is chosen)}\\
            x_i-\sum_{u=i \vee v=i}x_{uv} \leq 0 && \text{(forbid isolated nodes)}\\
            n x_{uv} + \ell_v - \ell_u \geq 1 - n(1-x_{vu}) && \text{(enforce increasing labels)}\\
            n x_{vu} + \ell_u - \ell_v \geq 1 - n(1-x_{uv}) && \text{(enforce increasing labels)}\\
            \end{align*}
    """        
    global var2edge
    global edge2var

    # Create model
    m = Model("Steiner Tree")  
    m.Params.LazyConstraints = 1
    
    # Add variables for edges and nodes
    G.setEdgeVars(m.addVars(G.G.edges(), vtype=gurobipy.GRB.BINARY))
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))
    
    m.update()    
    
    # abbreviations
    edges = G.edge_variables
    nodes = G.node_variables

    var2edge = dict(zip(edges.values(), edges.keys()))
    edge2var = edges
    
    # set objective: minimise the sum of the weights of edges selected for the solution
    m.setObjective(gurobipy.quicksum([edge_var * G.G.edges[edge][weight] for edge, edge_var in edges.items()]), GRB.MINIMIZE)

    # equality constraints for terminals (each terminal needs to be chosen, i.e. set it's value to 1)
    for node, node_var in nodes.items():
        # the outer loop makes sure that terminals that are not in the graph are ignored
        if node in terminals:
            m.addConstr(node_var == 1)

    # restrict number of edges, at max one edge between each pair of nodes
    m.addConstr(gurobipy.quicksum(nodes.values()) - gurobipy.quicksum(edges.values()) == 1)

    
    # if edge is chosen, both adjacent nodes need to be chosen
    for edge, edge_var in edges.items():
        m.addConstr(2*edge_var - nodes[edge[0]] - nodes[edge[1]] <= 0)

    # prohibit isolated vertices
    for node, node_var in nodes.items():
        edge_vars = [edge_var for edge, edge_var in edges.items() if (node==edge[0]) or (node==edge[1])]
        m.addConstr(node_var - gurobipy.quicksum(edge_vars) <= 0)
        
    m.update()

    return m

def callback_cycle(model, where):
    """ Callback insert constraints to forbid cycles in solution candidates
    """
    if where == gurobipy.GRB.Callback.MIPSOL: 
        # check for cycles whenever a new solution candidate is found
        variables = model.getVars()
        cur_sol = model.cbGetSolution(variables)

        # create graph from current solution
        solution = [var2edge[variables[i]] for i in range(len(variables)) if (cur_sol[i] > 0.5) and (variables[i]in var2edge)]
        G2 = nx.Graph()
        G2.add_edges_from(solution)
        
        try:
            # find a cycle in the solution
            cycle = nx.find_cycle(G2)
            cycle_idx = [edge if edge in var2edge.values() else (edge[1], edge[0]) for edge in cycle]
            
            # add new constraint
            model.cbLazy(gurobipy.quicksum([edge2var[edge] for edge in cycle_idx]) <= len(cycle_idx)-1)

        except:
            # do nothing if no cycle was found
            return

def extractSolution(G, model):
    r""" Get the optimal Steiner tree in G 
    
        :param G: a weighted ILPGraph
        :param model: a solved Gurobi model for the minimum Steiner tree problem
            
        :return: the edges of an optimal Steiner tree connecting all terminals in G
    """
    solution = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]

    return solution
# -

