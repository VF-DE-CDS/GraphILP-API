from numpy import ones


def get_heuristic(S):
    """ Greedy heuristic for the set packing problem

    Iteratively add the set with highest size-to-weight ratio which does not contain an element
    that is already covered to the solution.

    :param S: a weighted :py:class:`~graphilp.imports.ilpsetsystem.ILPSetSystem`

    :return: a list of disjoint sets of the set system
    """
    # abbreviations
    set_names = list(S.S.keys())
    set_index = range(len(S.S))
    set_sizes = sum(S.M)

    # which elements of the universe are not yet covered by the solution?
    not_covered = ones((len(S.U),), dtype=int)

    # all sets can still be used
    sets = set(set_index)

    # start with an empty result
    result = []

    # while there are still
    while len(sets) > 0:

        # pick most efficient set
        chosen_set = min([(set_sizes[_set] / S.S[set_names[_set]]['weight'], _set) for _set in sets])[1]
        result.append(chosen_set)

        # update which elements are not yet covered
        not_covered = not_covered * (1 - S.M[:, chosen_set])

        # remove all sets covering an element already covered by a set in the solution
        remove_sets = {_set for _set in set_index if sum((1 - not_covered) * S.M[:, _set]) > 0}
        sets = sets.difference(remove_sets)

    return [set_names[s] for s in result]
