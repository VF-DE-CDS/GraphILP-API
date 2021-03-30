from numpy import ones


def get_heuristic(S, k=None):
    """ Greedy heuristic for the set cover problem

        If paramter k is specified, the problem turns into a k-cover problem.
        In this case, the heuristic greedily approximates the maximal number of vertices that can
        be covered with at most k sets otherwise there is no limit on the number of sets.

        :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`
        :param k: maximal number of sets to use

        :return: a list of sets approximating the set cover problem
    """

    # set upper bound for number of sets to be chosen
    if k is None:
        k = len(S.S)

    # abbreviations
    set_names = list(S.S.keys())
    set_index = range(len(S.S))
    set_sizes = sum(S.M)

    # which elements of the universe are not yet covered by the solution?
    not_covered = ones((len(S.U),), dtype=int)

    # all sets can still be used
    sets = set(set_index)

    result = []

    # while there are elements to be covered and sets to choose from
    while (sum(not_covered) > 0) and (len(result) < k):

        # pick most efficient set and add it to the solution
        chosen_set = min([(S.S[set_names[_set]]['weight'] / set_sizes[_set], _set) for _set in sets])[1]
        result.append(chosen_set)

        # update which elements are not yet covered
        not_covered = not_covered * (1 - S.M[:, chosen_set])

        # remove chosen set
        sets.remove(chosen_set)

    return [set_names[s] for s in result]
