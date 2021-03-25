# +
from gurobipy import *
import numpy as np

def createModel(S, A, W):
    r""" Greate an ILP for the knapsack problem
    
    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`.
    :param A: Sparse weight matrix compressed by rows. 
    :param W: Size of each Knapsack
    
    TODO 
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    
    ILP:
    """
    
    # Create model
    m = Model("graphilp_max_knapsack")  
    
    # Add variables
    len_S = len(S.S)
    len_U = len(S.U)
    x = m.addMVar(shape=len_S, vtype=GRB.BINARY, name="x")
    S.setSystemVars(x)
    m.update()
    
    # set weight vector 
    obj = np.array([val['value'] for _set,val in S.S.items()])
    
    # Add constraints for covering
    m.addConstr(A @ x <= W, name="packing")
    
    # set optimisation objective: maximize weight of the set packing  
    m.setObjective(obj @ x, GRB.MAXIMIZE)
    
    return m

def extractSolution(S, model):
    r""" Get a list of items contained in the solution.
    
    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param model: a solved Gurobi model for the knapsack problem
            
    :return: Items contained in the knapsack solution
    :rtype: list of indeces
    """
    iterate = list(range(len(S.S)))
    knapsack = [list(S.S.keys())[i] for i in iterate if S.system_variables.X[i] > 0.5 ]
    
    return knapsack
