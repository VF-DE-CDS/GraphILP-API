import networkx as nx
import graphilp.network.reductions.pcst_utilities as pcst_utilities


def ntd1(G, terminals):
    """
    Delete all non-Terminals with degree one and their corresponding edges.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param terminals: A list of all terminals
    """
    nodes_to_remove = [n[0] for n in G.nodes(data=True) if G.degree[n[0]] == 1 and n[0] not in terminals]
    G.remove_nodes_from(nodes_to_remove)




#Lösche alle Knoten mit Grad 2, die keine Terminals sind (Aus dem Proktikumsbericht von Morris)
def ntd2(G, terminals):
    nodes_to_remove = [n for n in G.nodes(data=True) if G.degree[n[0]] == 2 and n[0] not in terminals]
    for node in nodes_to_remove:
        #Diese if-Abfrage braucht man, wenn bereits durch vorherige Schritte so Knoten entfernt wurden, dass ein ursprünglich zu entfernender Knoten nun nur noch einen Nachbarn hat und man daher keine Kante einfügen muss. Außerdem kann ein Knoten den gleichen nachbarn haben, daher muss auf Adjazenz geprüft werden
        if len(G.adj[node[0]]) > 1:
            u, v = list(G.neighbors(node[0]))[0], list(G.neighbors(node[0]))[1]
            edgelength = G.get_edge_data(node[0], u).get('weight') + G.get_edge_data(node[0], v).get('weight')
            if not G.has_edge(u,v) or G.has_edge(u, v) and G.get_edge_data(u, v).get('weight') > edgelength:
                G.add_edge(u, v, weight=edgelength)
        G.remove_node(node[0])


#Lösche alle Knoten mit Grad 1, die Terminals sind (Aus dem Praktikumsbericht von Morris)
def td1(G, terminals, root):
    candidates = [t for t in terminals if G.degree[t] == 1 and t != root]
    nodes_to_remove = []
    for t in candidates:
        neighbour = list(G.neighbors(t))[0]
        edgelength = G.get_edge_data(t, neighbour)['weight']
        profit = G.nodes[t]['prize']
        #Case a:
        if profit <= edgelength:
            nodes_to_remove.append(t)
        #Case 2, Case 1 muss nicht behandelt werden, da der Knoten bei beiden Cases gelöscht wird am ende des Durchlaufs
        else:
            G.nodes[neighbour]['prize'] += profit - edgelength
            nodes_to_remove.append(t)
        G.remove_nodes_from(nodes_to_remove)

#Lösche ausgewählte Knoten mit Grad 2, die Terminals sind (Aus dem Proktikumsbericht von Morris)
def td2(G, root):
    terminals = pcst_utilities.computeTerminals(G)
    candidates = [t for t in terminals if G.degree[t] == 2 and t != root]
    #candidates = [n for n in G.nodes(data=True) if G.degree[n[0]] == 2 and len(G.adj[n[0]]) > 1 and n in terminals]
    nodes_to_remove = []
    for n in candidates:
        profit_candidate = G.nodes[n]["prize"]
        neighbors = list(G.neighbors(n))
        length_e1 = G.get_edge_data(n, neighbors[0])['weight']
        length_e2 = G.get_edge_data(n, neighbors[1])['weight']
        profit_terminals = [G.nodes[t]["prize"] for t in terminals if t != n]
        if profit_candidate <= min(length_e1, length_e2, max(profit_terminals)):
            nodes_to_remove.append(n)
            length_newEdge = length_e1 + length_e2 - profit_candidate
            G.add_edge(neighbors[0], neighbors[1], weight = length_newEdge)
    G.remove_nodes_from(nodes_to_remove)



def unconnectedComponent(G):
    terminals = pcst_utilities.computeTerminals(G)
    terminal_nodes = [t for t in terminals]
    if nx.number_connected_components(G) > 1:
        for comp in list(nx.connected_components(G)):
            delete_component = True
            for n in comp:
                if n in terminal_nodes:
                    delete_component = False
            if delete_component == True:
                [G.remove_node(n) for n in comp]



def basic_reductions(G, root):
    terminals = pcst_utilities.computeTerminals(G)
    ntd1(G, terminals)
    ntd2(G, terminals)
    td1(G, terminals, root)
    td2(G, root)
    unconnectedComponent(G)

if __name__ == '__main__':
    if __name__ == '__main__':
        G = nx.Graph()

        G.add_nodes_from([
            (1, {'prize': 6}),
            (2, {'prize': 0}),
            (3, {'prize': 0}),
            (4, {'prize': 6}),
            (5, {'prize': 0}),
            (6, {'prize': 0}),
            (7, {'prize': 1}),
            (8, {'prize': 0}),
            (9, {'prize': 2})
        ])

        G.add_edges_from([(1, 2, {'weight': 3}), (1, 5, {'weight': 4}), (2, 3, {'weight': 1}),
                          (2, 4, {'weight': 4}), (3, 4, {'weight': 1}), (5, 6, {'weight': 2}),
                          (5, 7, {'weight': 1}), (6, 4, {'weight': 7}), (7, 8, {'weight': 2}),
                          (8, 4, {'weight': 3}), (7, 9, {'weight': 30})
                          ])
    print(G.number_of_edges())


    pcst_utilities.draw(G)
    basic_reductions(G)
    pcst_utilities.draw(G)





