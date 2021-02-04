# +
from gurobipy import *
import networkx as nx

node_list = None
edge_list = None
edge_dict = None
rev_edge_dict = None
def createModel(G, start_terminal, cycleBasis:bool = False, nodeColoring: bool = False):    
    """ Create an ILP for the linear Steiner Problem. The model can be seen in Paper Chapter 3.0. This model
    doesn't implement tightened labels.
    Arguments:            G -- an ILPGraph                    
    Returns:              a Gurobi model     
    """        
    # Create model
    m = Model("PCST")        
    
    m.Params.LazyConstraints = 1
    # Add variables for edges and nodes
    global node_list, edge_list, edge_dict, rev_edge_dict
    node_list = G.G.nodes()
    edge_list = G.G.edges()
    tst = set(edge_list)
    G.G.remove_edges_from([(u, v) for (u, v) in edge_list if (v, u) in tst])
    edge_list = list(G.G.edges())
    edge_dict = dict(enumerate(edge_list))
    rev_edge_dict = dict(zip(edge_dict.values(), edge_dict.keys()))

    # Variable definition
    for node in node_list:
        m.addVar(vtype=gurobipy.GRB.BINARY, name="node_" + str(node))
        m.addVar(vtype=gurobipy.GRB.BINARY, name="nodecolour_" + str(node))

    # create edge variables
    for edge in edge_list:
        G.setEdgeVars(m.addVar(vtype=gurobipy.GRB.BINARY, name="edge_" + str(rev_edge_dict[edge])))
    m.update()    

    m.setObjective(
        gurobipy.quicksum([n[1]['prize'] * m.getVarByName("node_" + str(n[0])) for n in node_list(data=True) if n[1]['prize'] > 0])\
        - gurobipy.quicksum([G.G.edges[u,v]['weight'] * m.getVarByName("edge_" + str(rev_edge_dict[(u,v)])) for (u, v) in edge_list]),\
        GRB.MAXIMIZE)

    # Enforce a root
    m.addConstr(m.getVarByName("node_" + str(start_terminal)) == 1)

    # restrict number of edges
    m.addConstr(  gurobipy.quicksum([m.getVarByName("node_" + str(node)) for node in node_list])\
            - gurobipy.quicksum([m.getVarByName("edge_" + str(rev_edge_dict[edge])) for edge in edge_list]) == 1)
    

    # if edge is chosen, both adjacent nodes need to be chosen
    for edge in edge_list:
        m.addConstr(  2*m.getVarByName("edge_" + str(rev_edge_dict[edge])) - m.getVarByName("node_" + str(edge[0]))\
                - m.getVarByName("node_" + str(edge[1])) <= 0 )

    # prohibit isolated vertices
    for node in node_list:
        edge_vars = [m.getVarByName("edge_" + str(rev_edge_dict[edge])) for edge in edge_list if (node==edge[0]) or (node==edge[1])]
        m.addConstr(m.getVarByName("node_" + str(node)) - gurobipy.quicksum(edge_vars) <= 0)

    if (nodeColoring == True):
        for edge in edge_list:
            m.addConstr(  m.getVarByName("edge_" + str(rev_edge_dict[edge])) - m.getVarByName("nodecolour_" + str(edge[0]))\
                        - m.getVarByName("nodecolour_" + str(edge[1])) <= 0 )
            m.addConstr(  m.getVarByName("edge_" + str(rev_edge_dict[edge])) + m.getVarByName("nodecolour_" + str(edge[0]))\
                        + m.getVarByName("nodecolour_" + str(edge[1])) <= 2 )

    if (cycleBasis == True):
        cycles = nx.cycle_basis(G.G)
        for cycle_list in cycles:
            cycle = []
            for pos in range(len(cycle_list)):
                cycle.append((cycle_list[pos], cycle_list[(pos+1)%len(cycle_list)]))
            cycle_idx = [edge if edge in edge_list else (edge[1], edge[0]) for edge in cycle]
            m.addConstr(gurobipy.quicksum([m.getVarByName("edge_" + str(rev_edge_dict[edge])) for edge in cycle_idx]) <= len(cycle_idx)-1)
        
    m.update()

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
    edge_list = G.G.edges()
    tst = set(edge_list)
    G.G.remove_edges_from([(u, v) for (u, v) in edge_list if (v, u) in tst])
    edge_list = list(G.G.edges())
    edge_dict = dict(enumerate(edge_list))
    rev_edge_dict = dict(zip(edge_dict.values(), edge_dict.keys()))
    
    solution = [edge_dict[int(model.getVarByName("edge_" + str(rev_edge_dict[edge])).VarName.split('_')[1])] for edge in edge_list\
        if model.getVarByName("edge_" + str(rev_edge_dict[edge])).X > 0.5]

    return solution
