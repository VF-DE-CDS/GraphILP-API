# +
import numpy as np
import scipy.sparse as sp
from gurobipy import *

def createModel(S):
    r""" Greate an ILP for the k-coverage problem
    
    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param A: Sparse covering matrix compressed by rows. Rows are Nodes and Columns are the Sets covering the Nodes 

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    
    ILP:
        .. math::
            :nowrap:
            
            \begin{align*}
            \min \sum_{s \in S} x_{s} \\
            \text{s.t.} &&\\
            \forall e \in E: \sum_{S:e \in S}x_{s} \leq 1 && \text{(cover every element of the universe)}\\
            \forall s \in S: x_{s} \in \{0,1\} && \text{(exactly one outgoing edge)}\\
            \sum_{(s, v) \in E}x_{sv} = 1 && \text{(every set is either in the set cover (1), otherwise 0)}\\
            \end{align*}
    """
    
    # Create model
    m = Model("graphilp_min_set_cover")  
    
    # Add variables
    len_x = len(S.S)
    len_b = len(S.U)
    A = S.M
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
            
    :return: Sets of the optimal Set cover solution
    :rtype: list of indeces
    """
    iterate = list(range (len(S.S)))
    set_cover = [list(S.S.keys())[i] for i in iterate if S.system_variables.X[i] > 0.5 ]
    
    return set_cover
