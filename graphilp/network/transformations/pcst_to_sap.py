import networkx as nx
import graphilp.network.reductions.pcst_utilities as pu

def steiner_arborescence_transformation(G, forced_terminals):
    """
    Transforms a given PCSTP instance into a Steiner Arborescence Problem instance.
    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param forced_terminals: list of terminals that have to be connected
    :return:
        G_sa: Transformed instance
        artificial_root: New root of the transformed instance
    """

    G_sa = nx.DiGraph()
   # G_sa.add_nodes_from(G.nodes)

    for n in G.nodes(data = True):
        G_sa.add_nodes_from([n])


    # add arcs
    for u, v, weight in G.edges(data='weight'):
        cost_u_v = weight
        prize_v = G.nodes[v]['prize']
        prize_u = G.nodes[u]['prize']

        G_sa.add_weighted_edges_from([[u, v, cost_u_v - prize_v],
                                      [v, u, cost_u_v - prize_u]])
    artificial_root = max(G.nodes()) + 1
    G_sa.add_nodes_from([(artificial_root, {"prize": 0})])
    # add arcs from articial root to terminals
    if forced_terminals == []:
        for t in pu.compute_terminals(G_sa):
            G_sa.add_weighted_edges_from([[artificial_root, t, -G_sa.nodes[t]['prize']]])
    else:
        for node in forced_terminals:
            G_sa.add_weighted_edges_from([[artificial_root, node, -G.nodes[node]['prize']]])

    return G_sa, artificial_root
