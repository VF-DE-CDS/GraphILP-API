# +
from gurobipy import *
import networkx as nx

def createModel(G, forced_terminals = [], weight = 'weight', prize = 'prize',
                cycleBasis:bool = False, nodeColoring: bool = False):    
    r""" Create an ILP for the Prize Collecting Steiner Tree Problem. 
    
    The model can be seen in Paper Chapter 3.0. This model
    doesn't implement tightened labels.
    
    :param G: an ILPGraph
    :param forced_terminals: list of terminals that have to be connected
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost
    :param prize: name of the argument in the node dictionary of the graph used to store node prize values

    :return: a Gurobi model   
    
    ILP: 
        .. math::
            :nowrap:

            \begin{align*}
            \max \sum_{i \in V} p_i x_i- \sum_{(i,j) \in E} w_{ij} x_{ij}\\
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
    
    # ensure that input is a directed graph
    if type(G.G) != nx.classes.digraph.DiGraph:
        G.G = nx.DiGraph(G.G)
        
    # create model
    m = Model("Steiner Tree")        
    
    n = G.G.number_of_nodes()

    # create reverse edge for every edge in the graph
    for edge in G.G.edges():
        G.G.add_edge(*edge[::-1])

    G.setNodeVars(m.addVars(G.G.nodes(), vtype = gurobipy.GRB.BINARY))
    G.setEdgeVars(m.addVars(G.G.edges(), vtype = gurobipy.GRB.BINARY))

    # node label variables used to avoid cycles 
    G.setLabelVars(m.addVars(G.G.nodes(), vtype = gurobipy.GRB.INTEGER, lb = 1, ub = n))

    m.update()  

    # abbreviations
    edges = G.edge_variables
    nodes = G.node_variables
    labels = G.label_variables
    edge2var = dict(zip(edges.keys(), edges.values()))

    # set objective: minimise the sum of the weights of edges selected for the solution
    m.setObjective(gurobipy.quicksum([G.G.nodes[node].get(prize, 0) * node_var for node, node_var in nodes.items()])
                   - gurobipy.quicksum([edge_var * G.G.edges[edge][weight] for edge, edge_var in edges.items()]), 
                   GRB.MAXIMIZE)
    
    # equality constraints for forced terminals (each terminal needs to be chosen, i.e., set its value to 1)
    for node, node_var in nodes.items():
        # the outer loop makes sure that terminals that are not in the graph are ignored
        if node in forced_terminals:
            m.addConstr(node_var == 1)

    # restrict number of edges, at max one edge between each pair of nodes
    m.addConstr(gurobipy.quicksum(nodes.values()) - gurobipy.quicksum(edges.values()) == 1)

    # at most one direction per edge can be chosen
    # runtime can probably be greatly improved if iterating is done in a smarter way
    for edge, edge_var in edges.items():
        reverseEdge = edge[::-1]
        rev_edge_var = edge2var.get(reverseEdge)
        if rev_edge_var != None:
            m.addConstr(edge_var + rev_edge_var <= 1)

    # if edge is chosen, both adjacent nodes need to be chosen
    for edge, edge_var in edges.items():
        m.addConstr(2*edge_var - nodes[edge[0]] - nodes[edge[1]] <= 0)

    # prohibit isolated vertices
    for node, node_var in nodes.items():
        edge_vars = []
        for edge, edge_var in edges.items():
            # If the node is startpoint or endpoint of the edge, add the edge
            # to the array of edge variables
            # Since the edges variable containt both directions, we can write this much short than
            # in the previous formulation
            if (node == edge[0] or node == edge[1]):
                edge_vars.append(edge_var)
        m.addConstr(node_var - gurobipy.quicksum(edge_vars) <= 0)

    
    # labeling constraints: enforce increasing labels in edge direction of selected edges 
    for edge, edge_var in edges.items():
        reverseEdge = edge[::-1]
        edge_var_rev = edge2var.get(reverseEdge)
        if edge_var_rev != None:
            m.addConstr( n * edge_var_rev + labels[edge[1]] - labels[edge[0]] >= 1 - n*(1 - edge_var))
            m.addConstr( n * edge_var + labels[edge[0]] - labels[edge[1]] >= 1 - n*(1 - edge_var_rev))

    # allow only one arrow into each node
    for node in nodes:
        constraint_edges =  [(u, v) for (u, v) in edges.keys() if v == node]
        m.addConstr(gurobipy.quicksum([edges[e] for e in constraint_edges]) <= 1)
    
    return m

def callback_cycle(model, where):
    if where == GRB.Callback.MIPSOL:
        variables = model.getVars()
        cur_sol = model.cbGetSolution(variables)
        
        solution = [edge_dict[int(variables[i].VarName.split('_')[1])] for i in range(len(variables)) if (cur_sol[i] > 0.5) and (variables[i].VarName.split('_')[0] == 'edge')]
        G2 = nx.Graph()
        G2.add_edges_from(solution)
        try:
            cycle = nx.find_cycle(G2)
            cycle_idx = [edge if edge in edge_list else (edge[1], edge[0]) for edge in cycle]
            model.cbLazy(gurobipy.quicksum([model.getVarByName("edge_" + str(rev_edge_dict[edge])) for edge in cycle_idx]) <= len(cycle_idx)-1)
        except:
            return 
        
def extractSolution(G, model):
    """ Get the optimal tour in G 
    
        Arguments:
            G     -- a weighted ILPGraph
            model -- a solved Gurobi model for min/max Path asymmetric TSP 
            
        Returns:
            the edges of an optimal tour/path in G 
    """
    solution = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]

    return solution


# -


