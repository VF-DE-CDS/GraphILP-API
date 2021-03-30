# +
from gurobipy import *
import numpy as np

def createModel(S, k):
    r""" Greate an ILP for the k-cover problem
    
    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param k: maximal number of sets in solution

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    
    ILP:
        Let :math:`S` be the collection of sets in the set system and :math:`U` the underlying universe.
    
        .. math::
            :nowrap:
            
            \begin{align*}
            \min \sum_{s \in S} x_{s} \\
            \text{s.t.} &&\\
            \forall u \in U: \sum_{s:u \in s}x_{s} \geq 1 && \text{(cover every element of the universe)}\\
            \sum_{s \in S} x_{s} \leq k && \text{(use at most k sets)}\\
            \forall s \in S: x_{s} \in \{0,1\} && \text{(every set is either in the set cover or not)}\\
            \end{align*}
    """
    
    # Create model
    m = Model("graphilp_k_coverage")  
    
    # Add variables for sets
    len_S = len(S.S)
    len_U = len(S.U)
    x = m.addMVar(shape=len_S, vtype=GRB.BINARY, name="x")
    S.setSystemVars(x)
    m.update()
    
    # Add variables for universe
    y = m.addMVar(shape=len_U, vtype=GRB.BINARY, name="y")
    S.setUniverseVars(y)
    m.update()
    
    # set weight vector 
    obj = np.array([val['weight'] for _set, val in S.U.items()])
    
    # Add constraints for covering
    m.addConstr(S.M @ x >= y, name="covering")
    
    # Add constraints for packing
    b = np.ones((len_S,), dtype=int)
    m.addConstr(b @ x <= k, name="packing")
    
    # set optimisation objective: maximize weight of the set cover 
    m.setObjective(obj @ y, GRB.MAXIMIZE)
    
    return m

def extractSolution(S, model):
    """ Get a list of sets comprising the k-cover
    
    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param model: a solved Gurobi model for k coverage

    :return: list of sets contained in the solution of the k-cover
    """
    iterate = list(range(len(S.S)))
    set_cover = [list(S.S.keys())[i] for i in iterate if S.system_variables.X[i] > 0.5]
    
    return set_cover 
