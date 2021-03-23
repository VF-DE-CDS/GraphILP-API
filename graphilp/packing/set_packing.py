# +
from gurobipy import *
import numpy as np

def createModel(S, A):
    r""" Greate an ILP for the weighted set packing problem
    
    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param A: TODO

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    
    ILP:
    
    """
    
    # Create model
    m = Model("graphilp_max_set_packing")  
    
    # Add variables
    len_x = len(S.S)
    len_b = len(S.U)
    x = m.addMVar(shape=len_x, vtype=GRB.BINARY, name="x")
    S.setSystemVars( x)
    m.update()
    
    # Add vector b for the right-hand side
    b = np.ones((len_b,), dtype=int)
    
    # set weight vector 
    obj = np.array([val['weight'] for _set, val in S.S.items()])
    
    # Add constraints
    m.addConstr(A @ x <= b, name="c")
    
    # set optimisation objective: maximize weight of the set packing  
    m.setObjective(obj @ x, GRB.MAXIMIZE)
    
    return m

def extractSolution(S, model):
    """ Get a list of sets comprising a set packing
    
    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param model: a solved Gurobi model for weighted set packing
            
    :return: a list of sets comprising a set packing
    """
    iterate = list(range(len(S.S)))
    set_cover = [list(S.S.keys())[i] for i in iterate if S.system_variables.X[i] > 0.5 ]
    
    return set_cover
