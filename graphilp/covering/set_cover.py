# +
import numpy as np
import scipy.sparse as sp
from gurobipy import *

def createModel(S, A):
    """ Greate an ILP for the weighted set cover problem

    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param A: TODO

    :returns: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    """
    
    # Create model
    m = Model("graphilp_min_set_cover")  
    
    # Add variables
    len_x = len(S.S)
    len_b = len(S.U)
    x = m.addMVar(shape=len_x, vtype=GRB.BINARY, name="x")
    S.setSystemVars(x)
    m.update()
    
    # Add  vector b for the right-hand side
    b = np.ones((len_b,), dtype=int)
    # set weight vector 
    obj = np.array([val['weight'] for _set,val in S.S.items()])
    
    # Add constraints
    m.addConstr(A @ x >= b, name="c")
    
    # set optimisation objective: minimize cardinality of the set cover  
    m.setObjective(obj @ x, GRB.MINIMIZE)
    
    return m

def extractSolution(S, model):
    """ Get a list of sets comprising a set cover
    
    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param model: a solved Gurobi model for weighted set packing
            
    :return: a list of sets comprising a set cover
    """
    iterate = list(range (len(S.S)))
    set_cover = [list(S.S.keys())[i] for i in iterate if S.system_variables.X[i] > 0.5 ]
    
    return set_cover
