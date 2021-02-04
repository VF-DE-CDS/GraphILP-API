# +
from gurobipy import *
import networkx as nx

node_list = None
edge_list = None
edge_dict = None
rev_edge_dict = None

def createModel(G, terminals, cycleBasis: bool = False, nodeColoring: bool = False):    
    """ Create an ILP for the linear Steiner Problem. The model can be seen in Paper Chapter 3.0. This model
    doesn't implement tightened labels.
    Arguments:            G -- an ILPGraph                    
    Returns:              a Gurobi model     
    """        
    # Create model
    m = Model("Steiner Tree")        
    
    # Add variables for edges and nodes
    global node_list, edge_list, edge_dict, rev_edge_dict
    node_list = G.G.nodes()
    edge_list = G.G.edges()
    edge_dict = dict(enumerate(edge_list))
    rev_edge_dict = dict(zip(edge_dict.values(), edge_dict.keys()))

    # create node variables
    for node in node_list:
        m.addVar(vtype=gurobipy.GRB.BINARY, name="node_" + str(node))
        m.addVar(vtype=gurobipy.GRB.BINARY, name="nodecolour_" + str(node))

    # create edge variables
    for edge in edge_list:
        m.addVar(vtype=gurobipy.GRB.BINARY, name="edge_" + str(rev_edge_dict[edge]))

    m.update()    

    m.setObjective(gurobipy.quicksum([edge_list[u,v]['weight'] * m.getVarByName("edge_" + str(rev_edge_dict[(u,v)])) for (u, v) in edge_list]),\
                  GRB.MINIMIZE)

    # equality constraints for terminals (each terminal needs to be chosen)
    for node in node_list:
        if node in terminals:
            m.addConstr(m.getVarByName("node_" + str(node)) == 1)

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

    
    return m

    
def callback_cycle(model, where):
    #if where == gurobipy.GRB.Callback.MIPSOL:
    if where == gurobipy.GRB.Callback.MIPNODE:
        variables = model.getVars()
        #cur_sol = model.cbGetSolution(variables)
        cur_sol = model.cbGetNodeRel(variables)
        
        solution = [edge_dict[int(variables[i].VarName.split('_')[1])] for i in range(len(variables)) if (cur_sol[i] > 0.5) and (variables[i].VarName.split('_')[0] == 'edge')]
        G2 = nx.Graph()
        G2.add_edges_from(solution)
        try:
            cycle = nx.find_cycle(G2)
            cycle_idx = [edge if edge in edge_list else (edge[1], edge[0]) for edge in cycle]
            forbidden_cycles.append(cycle_idx)
            #model.addConstr(gurobipy.quicksum([model.getVarByName("edge_" + str(rev_edge_dict[edge])) for edge in cycle_idx]) <= len(cycle_idx)-1)
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
    print(solution)
    return solution
# -


