from gurobipy import Model, GRB
from numpy import ones, array


def create_model(S, warmstart=[]):
    r""" Create an ILP for the weighted set packing problem

    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param warmstart: a list of disjoint sets in the set system

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        Let :math:`M` be the incidence matrix of the set system, :math:`w` the vector of weights associated to
        the sets of the system, :math:`x` a vector indicating which set is selected, and :math:`1` a vector of ones.

        .. math::
            :nowrap:

            \begin{align*}
            \max w^{\top}x\\
            \text{s.t.} &&\\
            Mx \leq 1 && \text{(each element of the universe is in at most one set)}\\
            \end{align*}
    """

    # Create model
    m = Model("graphilp_max_set_packing")

    # Add variables
    x = m.addMVar(shape=len(S.S), vtype=GRB.BINARY, name="x")
    S.set_system_vars(x)
    m.update()

    # Add vector b for the right-hand side
    b = ones((len(S.U),), dtype=int)

    # set weight vector
    obj = array([val.get('weight', 1) for _set, val in S.S.items()])

    # Add constraints
    m.addConstr(S.M @ x <= b, name="c")

    # set optimisation objective: maximize weight of the set packing
    m.setObjective(obj @ x, GRB.MAXIMIZE)

    # set warmstart
    if len(warmstart) > 0:
        sets = list(S.S.keys())
        for pos in range(len(sets)):
            if sets[pos] in warmstart:
                x[pos].Start = 1
            else:
                x[pos].Start = 0

    m.update()

    return m


def extract_solution(S, model):
    """ Get a list of sets comprising a set packing

    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param model: a solved Gurobi model for weighted set packing

    :return: a list of sets comprising a set packing
    """
    iterate = list(range(len(S.S)))
    set_cover = [list(S.S.keys())[i] for i in iterate if S.system_variables.X[i] > 0.5]

    return set_cover
