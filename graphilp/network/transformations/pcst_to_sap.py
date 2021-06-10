import networkx as nx
import graphilp.network.reductions.pcst_utilities as pu

def steiner_arborescence_transformation(G, forced_terminals):
    """
    transforms self.G into a directed graph for steiner arborescence problem
    """
    G_sa = nx.DiGraph()
    G_sa.add_nodes_from(G.nodes())

    artificial_root = max(G.nodes()) + 1
    G_sa.add_node(artificial_root)

    # add arcs
    for u, v, weight in G.edges(data='weight'):
        cost_u_v = weight
        prize_v = G.nodes[v]['prize']
        prize_u = G.nodes[u]['prize']

        G_sa.add_weighted_edges_from([[u, v, cost_u_v - prize_v],
                                      [v, u, cost_u_v - prize_u]])

    # add arcs from articial root to terminals
    if forced_terminals == []:
        for t in pu.computeTerminals(G):
            G_sa.add_weighted_edges_from([[artificial_root, t, -G.nodes[t]['prize']]])
    else:
        for node in forced_terminals:
            G_sa.add_weighted_edges_from([[artificial_root, node, -G.nodes[node]['prize']]])

    return G_sa, artificial_root

def translate_to_original(self, G_sa):
    """
    translates a msa solution back to original non-directed graph
    G_sa: steiner arb. solution
    """
    G_translated = nx.Graph()
    G_translated.add_nodes_from(self.G.nodes())
    prizes = dict(self.G.nodes(data=self.node_attr_name))
    nx.set_node_attributes(G_translated, values=prizes, name='prize')

    for u, v in G_sa.edges():

        # get cost of edge in original graph G
        if (u, v) in self.G.edges():
            edge = (u, v)
        elif (v, u) in self.G.edges():
            edge = (v, u)
        else:
            if u != self.root_sa and v != self.root_sa:
                print('Could neither find {0} nor {1} in edges.'.format((u, v), (v, u)))
                continue

        cost = self.G.get_edge_data(edge[0], edge[1])[self.edge_attr_name]
        G_translated.add_weighted_edges_from([[edge[0], edge[1], cost]])

    return G_translated