from numpy import array, ones
from gurobipy import Model, GRB


def create_model(S, warmstart=[]):
    r""" Greate an ILP for the set cover problem

    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param warmstart: a list of sets forming a cover

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        Let :math:`S` be the collection of sets in the set system, :math:`U` the underlying universe,
        and :math:`w_s` the weight of set :math:`s \in S`.

        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{s \in S} w_{s} x_{s} \\
            \text{s.t.} &&\\
            \forall u \in U: \sum_{s:u \in s}x_{s} \geq 1 && \text{(cover every element of the universe)}\\
            \forall s \in S: x_{s} \in \{0,1\} && \text{(every set is either in the set cover or not)}\\
            \end{align*}
    """

    # Create model
    m = Model("graphilp_min_set_cover")

    # Add variables
    len_x = len(S.S)
    len_b = len(S.U)
    x = m.addMVar(shape=len_x, vtype=GRB.BINARY, name="x")
    S.set_system_vars(x)
    m.update()

    # add  vector b for the right-hand side
    b = ones((len_b,), dtype=int)
    # set weight vector
    obj = array([val.get('weight', 1) for _set, val in S.S.items()])

    # add constraints
    m.addConstr(S.M @ x >= b, name="c")

    # set optimisation objective: minimize weight of the set cover
    m.setObjective(obj @ x, GRB.MINIMIZE)

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
    """ Get a list of sets comprising a set cover

    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param model: a solved Gurobi model for weighted set cover

    :return: sets of the optimal set cover solution
    """
    iterate = list(range(len(S.S)))
    set_cover = [list(S.S.keys())[i] for i in iterate if S.system_variables.X[i] > 0.5]

    return set_cover
