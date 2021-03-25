# +
from gurobipy import *
import numpy as np

def createModel(S, A, k):
    """ Greate an ILP for the k-coverage problem
    
    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param A: Sparse covering matrix compressed by rows. Rows are Nodes and Columns are the Sets covering the Nodes 
    :param k: Maximum amount of Sets in solution

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    
    ILP:
    
        .. math::
            :nowrap:
                \begin{align*}
                \min \sum_{s \in S} x_{s} \\
                \text{s.t.} &&\\
                \forall e \in U: \sum_{S:e \in S}x_{s} \geq 1 && \text{(cover every element of the universe)}\\
                \forall s \in S: x_{s} \in \{0,1\} && \text{(exactly one outgoing edge)}\\
                \sum_{(s, v) \in E}x_{sv} = 1 && \text{(every set is either in the set cover (1), otherwise 0)}\\
                \sum_{s \in S} x_{s} \leq k && \text{(Use maximum k sets)}\\
                \end{align*}
    """
    
    # Create model
    m = Model("graphilp_k_coverage")  
    
    # Add variables
    len_S = len(S.S)
    len_U = len(S.U)
    x = m.addMVar(shape=len_S, vtype=GRB.BINARY, name="x")
    S.setSystemVars(x)
    m.update()
    
    # Add vector b for the right-hand side
    y = m.addMVar(shape=len_U, vtype=GRB.BINARY, name="y")
    S.setUniverseVars(y)
    m.update()
    
    # set weight vector 
    obj = np.array([val['weight'] for _set,val in S.U.items()])
    
    # Add constraints for covering
    m.addConstr(A @ x >= y, name="cover")
    
    # Add constraints for packing
    b = np.ones((len_S,), dtype=int)
    m.addConstr(b @ x <= k, name="packing")
    
    # set optimisation objective: maximize weight of the set packing  
    m.setObjective(obj @ y, GRB.MAXIMIZE)
    
    return m

def extractSolution(S, model):
    """ Get a list of sets comprising the k - Cover
    
    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param model: a solved Gurobi model for k coverage

    :return: List of sets contained in the solution of the k - cover
    :rtype: list of int
    """
    iterate = list(range(len(S.S)))
    set_cover = [list(S.S.keys())[i] for i in iterate if S.system_variables.X[i] > 0.5 ]
    
    return set_coverdef 
