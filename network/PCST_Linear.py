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
    m = Model("Linear PCST")        
    m.Params.threads = 3
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
        m.addVar(vtype=gurobipy.GRB.INTEGER, lb=1, ub=len(node_list), name="label_" + str(node))
        m.addVar(vtype=gurobipy.GRB.BINARY, name="nodecolour_" + str(node))

    for edge in edge_list:
        m.addVar(vtype=gurobipy.GRB.BINARY, name="edge_" + str(edge[0]) + "_" + str(edge[1]))
        m.addVar(vtype=gurobipy.GRB.BINARY, name="edge_" + str(edge[1]) + "_" + str(edge[0]))

    m.update()    

    m.setObjective(
        gurobipy.quicksum([n[1]['prize'] * m.getVarByName("node_" + str(n[0])) for n in node_list(data=True) if n[1]['prize'] > 0])\
        - gurobipy.quicksum([G.G.edges[u,v]['weight'] * m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edge_list])\
        - gurobipy.quicksum([G.G.edges[u,v]['weight'] * m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u, v) in edge_list]),\
        GRB.MAXIMIZE)

    # at most one direction per edge can be chosen
    for (u,v) in edge_list:
        m.addConstr(m.getVarByName("edge_" + str(u) + "_" + str(v)) + m.getVarByName("edge_" + str(v) + "_" + str(u)) <= 1)

    # allow only one arrow into each node. Alternative formulation
    for node in node_list:
        edges =  [(u, v) for (u, v) in edge_list if v == node]
        edges += [(v, u) for (u, v) in edge_list if u == node]
        m.addConstr(gurobipy.quicksum([m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edges]) <= 1)

    # Enforce a root
    m.addConstr(m.getVarByName("node_" + str(start_terminal)) == 1)

    # enforce cirlce when graph is not connected
    m.addConstr(gurobipy.quicksum([m.getVarByName("node_" + str(node)) for node in node_list])\
            - gurobipy.quicksum([m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u,v) in edge_list])\
            - gurobipy.quicksum([m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u,v) in edge_list]) == 1)

    # if edge is chosen, both adjacent nodes need to be chosen
    for (u, v) in edge_list:
        m.addConstr(  2 * (m.getVarByName("edge_" + str(u) + "_" + str(v)) + m.getVarByName("edge_" + str(v) + "_" + str(u)))\
                - m.getVarByName("node_" + str(u))\
                - m.getVarByName("node_" + str(v)) <= 0 )

    # prohibit isolated vertices / nodes
    for node in node_list:
        edge_vars = [m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edge_list if (node==u) or (node==v)]\
                  + [m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u, v) in edge_list if (node==u) or (node==v)]
        m.addConstr(m.getVarByName("node_" + str(node)) - gurobipy.quicksum(edge_vars) <= 0)

    # enforce increasing labels
    n = len(node_list)
    for (u,v) in edge_list:
        m.addConstr(  n * m.getVarByName("edge_" + str(v) + "_" + str(u)) + m.getVarByName("label_" + str(v))\
                    - m.getVarByName("label_" + str(u)) >= 1 - n*(1-m.getVarByName("edge_" + str(u) + "_" + str(v))))
        m.addConstr(  n * m.getVarByName("edge_" + str(u) + "_" + str(v)) + m.getVarByName("label_" + str(u))\
                    - m.getVarByName("label_" + str(v)) >= 1 - n*(1-m.getVarByName("edge_" + str(v) + "_" + str(u))))


    if (nodeColoring == True):
        for edge in edge_list:
            m.addConstr(  m.getVarByName("edge_" + str(edge[0]) + "_" + str(edge[1])) - m.getVarByName("nodecolour_" + str(edge[0]))\
                        - m.getVarByName("nodecolour_" + str(edge[1])) <= 0 )
            
            
            m.addConstr(  m.getVarByName("edge_" + str(edge[0]) + "_" + str(edge[1])) + m.getVarByName("nodecolour_" + str(edge[0]))\
                        + m.getVarByName("nodecolour_" + str(edge[1])) <= 2 )
    
    if (cycleBasis == True):
        cycles = nx.cycle_basis(G.G)
        for cycle_list in cycles:
            cycle = []
            for pos in range(len(cycle_list)):
                cycle.append((cycle_list[pos], cycle_list[(pos+1)%len(cycle_list)]))
            cycle_idx = [edge if edge in edge_list else (edge[1], edge[0]) for edge in cycle]
            m.addConstr(gurobipy.quicksum([m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in cycle_idx]) <= len(cycle_idx)-1)

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


# -


