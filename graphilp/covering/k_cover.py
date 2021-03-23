# +
from gurobipy import *
import numpy as np

def createModel(S, A, k):
    """ Greate an ILP for the k-coverage problem
    
    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param A: TODO
    :param k: TODO

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    
    ILP:
    """
    
    # Create model
    m = Model("graphilp_k_coverage")  
    
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

def extractSolution(S, model):
    """ TODO
    
    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param model: a solved Gurobi model for k coverage

    :return: TODO
    """
    iterate = list(range(len(S.S)))
    set_cover = [list(S.S.keys())[i] for i in iterate if S.system_variables.X[i] > 0.5 ]
    
    return set_coverdef 
