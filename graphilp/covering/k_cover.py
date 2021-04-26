from gurobipy import Model, GRB
import numpy as np


def create_model(S, k, warmstart=[]):
    r""" Greate an ILP for the k-cover problem

    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param k: maximal number of sets in solution
    :param warmstart: a list of sets forming a cover

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        Let :math:`S` be the collection of sets in the set system, :math:`U` the underlying universe, and
        :math:`w_u` the weight of each element :math:`u \in U`.
        For each :math:`s \in S`, the decision variable :math:`x_s` indicates whether :math:`s` is part
        of the solution. For each :math:`u \in U`, the decision variable :math:`y_u` indicates whether
        :math:`u` is covered in the solution.

        .. math::
            :nowrap:

            \begin{align*}
            \max \sum_{u \in U} w_u y_u \\
            \text{s.t.} &&\\
            \forall u \in U: \sum_{s:u \in s}x_{s} \geq y_u && \text{(chosen sets cover elements of the universe)}\\
            \sum_{s \in S} x_{s} \leq k && \text{(use at most k sets)}\\
            \end{align*}
    """

    # Create model
    m = Model("graphilp_k_coverage")

    # Add variables for sets
    len_S = len(S.S)
    len_U = len(S.U)
    x = m.addMVar(shape=len_S, vtype=GRB.BINARY, name="x")
    S.set_system_vars(x)
    m.update()

    # Add variables for universe
    y = m.addMVar(shape=len_U, vtype=GRB.BINARY, name="y")
    S.set_universe_vars(y)
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

    # set warmstart
    if len(warmstart) > 0:

        for pos in range(len(S.U)):
            y[pos].Start = 0

        sets = list(S.S.keys())
        for pos in range(len(sets)):
            if sets[pos] in warmstart:
                x[pos].Start = 1

                covered = S.M[:, pos]
                for element in range(len(covered)):
                    if covered[element] > 0:
                        y[element].Start = 1
            else:
                x[pos].Start = 0

        m.update()

    return m


def extract_solution(S, model):
    """ Get a list of sets comprising the k-cover

    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
    :param model: a solved Gurobi model for k coverage

    :return: list of sets contained in the solution of the k-cover
    """
    iterate = list(range(len(S.S)))
    set_cover = [list(S.S.keys())[i] for i in iterate if S.system_variables.X[i] > 0.5]

    return set_cover
