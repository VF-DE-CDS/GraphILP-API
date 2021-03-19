# +
from gurobipy import *
import numpy as np

def createModel(SetCover, A):
    """ Greate an ILP for the weighted packing problem
    
        Arguments:
            SetCover     -- a weighted ILPSetSystem

        Returns:
            Gurobi model for weighted set packing
    """
    
    # Create model
    m = Model("setsystemilp_max_set_packing")  
    
    # Add variables
    len_x = len(SetCover.S)
    len_b = len(SetCover.U)
    x = m.addMVar(shape=len_x, vtype=GRB.BINARY, name="x")
    SetCover.setSystemVars( x)
    m.update()
    
    # Add  vector b for the right-hand side
    b = np.ones((len_b,), dtype=int)
    
    # set weight vector 
    obj = np.array([val['weight'] for _set,val in SetCover.S.items()])
    
    # Add constraints
    m.addConstr(A @ x <= b, name="c")
    
    # set optimisation objective: maximize weight of the set packing  
    m.setObjective(obj @ x, GRB.MAXIMIZE)
    
    return m

def extractSolution(SetCover, model):
    """ Get a list of sets comprising a set packing
    
        Arguments:
            SetCover     -- a weighted ILPSetSystem
            model        -- a solved Gurobi model for weighted set packing
            
        Returns:
            a list of sets comprising a set packing
    """
    iterate = list(range (  len(SetCover.S) ) )
    set_cover = [list(SetCover.S.keys())[i] for i in iterate if SetCover.system_variables.X[i] > 0.5 ]
    
    return set_cover
