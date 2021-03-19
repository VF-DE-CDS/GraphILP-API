# +
from gurobipy import *
import numpy as np

def createModel(SetCover, A, k):
    """ Greate an ILP for the k-coverage problem
    
        Arguments:
            SetSystem     -- a weighted ILPSetSystem

        Returns:
            Gurobi model for weighted set packing
    """
    
    # Create model
    m = Model("setsystemilp_max_set_packing")  
    
    # Add variables
    len_S = len(SetCover.S)
    len_U = len(SetCover.U)
    x = m.addMVar(shape=len_S, vtype=GRB.BINARY, name="x")
    SetCover.setSystemVars( x)
    m.update()
    
    # Add  vector b for the right-hand side
    y = m.addMVar(shape=len_U, vtype=GRB.BINARY, name="y")
    SetCover.setUniverseVars( y)
    m.update()
    
    # set weight vector 
    obj = np.array([val['weight'] for _set,val in SetCover.U.items()])
    # Add constraints for covering
    m.addConstr(A @ x >= y, name="cover")
    
    # Add constraints for packing
    b = np.ones((len_S,), dtype=int)
    m.addConstr(b @ x <= k, name="packing")
    
    # set optimisation objective: maximize weight of the set packing  
    m.setObjective(obj @ y, GRB.MAXIMIZE)
    
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
    
    return set_coverdef 
