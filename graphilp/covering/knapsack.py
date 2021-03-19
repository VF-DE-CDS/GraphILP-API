# +
from gurobipy import *
import numpy as np

def createModel(SetSystem, A, W):
    """ Greate an ILP for the knapsack problem
    
        Arguments:
         SetSystemstem     -- a weighted ILPSetSystem

        Returns:
            Gurobi model for knapsack problem
    """
    
    # Create model
    m = Model("setsystemilp_max_kapsack")  
    
    # Add variables
    len_S = len(SetSystem.S)
    len_U = len(SetSystem.U)
    x = m.addMVar(shape=len_S, vtype=GRB.BINARY, name="x")
    SetSystem.setSystemVars( x)
    m.update()
    
    
    # set weight vector 
    obj = np.array([val['value'] for _set,val in SetSystem.S.items()])
    
    # Add constraints for covering
    m.addConstr(A @ x <= W, name="packing")
    
    # set optimisation objective: maximize weight of the set packing  
    m.setObjective(obj @ x, GRB.MAXIMIZE)
    
    return m

def extractSolution(SetSystem, model):
    """ Get a list of sets comprising a set packing
    
        Arguments:
            SetCover     -- a weighted ILPSetSystem
            model        -- a solved Gurobi model for weighted set packing
            
        Returns:
            a list of sets comprising a set packing
    """
    iterate = list(range (  len(SetSystem.S) ) )
    knapsack = [list(SetSystem.S.keys())[i] for i in iterate if SetSystem.system_variables.X[i] > 0.5 ]
    
    return knapsack
