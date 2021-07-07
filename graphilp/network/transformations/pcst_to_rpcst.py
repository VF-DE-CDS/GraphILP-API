from graphilp.network.reductions.pcst_utilities import compute_terminals


def pcst_to_rpcst(G):
    """
    Routine to include a root to an PCSTP instance.
    For the dual ascent reduction technique,
    it is not possible to insert a node with very high profit and connect it to all nodes.
    The transformation algorithm is taken from the following source:
    Rehfeldt, Daniel, and Thorsten Koch.
    "On the exact solution of prize-collecting Steiner tree problems." (2020).
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :return
        G_r: Transformed instance
        terminals_fixed: All new forced terminals
        m: Sum of all profit of all terminals
        n: Root of the new instance
    """
    terminals = compute_terminals(G)
    terminals_proper = [t for t in terminals if
                        G.nodes[t]['prize'] > min([e.get('weight') for e in list(G.adj[t].values())])]
    terminals_unproper = [t for t in terminals if
                          G.nodes[t]['prize'] <= min([e.get('weight') for e in list(G.adj[t].values())])]
    terminals_fixed = []
    m = sum([G.nodes[t]['prize'] for t in terminals_proper])
    G_r = G.copy()
    for v in G_r.nodes:
        if v not in terminals_unproper:
            G_r.nodes[v]['prize'] = 0
    j = min(terminals_proper, key=lambda x: G.nodes[x]['prize'])
    n = G_r.number_of_nodes() + 1
    G_r.add_nodes_from([(n, {'prize': 0})])
    terminals_fixed.append(n)
    for t in terminals_proper:
        id = t + n
        G_r.add_nodes_from([(id, {'prize': 0})])
        G_r.add_edges_from([(n, t, {'weight': m}), (t, id, {'weight': m})])
        terminals_fixed.append(id)
    for t in terminals_proper:
        if t == j:
            continue
        id = t + n
        G_r.add_edges_from(
            [(t, j + n, {'weight': m + G.nodes[j]['prize']}), (id, j + n, {'weight': m + G.nodes[t]['prize']})])
    return G_r, terminals_fixed, m, n