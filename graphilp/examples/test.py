import networkx as nx
import pcst_fast
import graphilp.network.reductions.pcst_fast_interface_temp as pcst
from gurobipy import Model, GRB, quicksum
import gurobipy
import time
from graphilp.network import pcst_linear as pl
from graphilp.imports import networkx as imp_nx
from graphilp.imports import readFile as gf
from graphilp.network import pcst_linear as stp
from graphilp.network.reductions import pcst_basic_reductions as br
from graphilp.network.reductions import pcst_voronoi as vor
from graphilp.network.reductions import pcst_utilities as pu
from graphilp.network.reductions import pcst_dualAscent as da

if __name__ == '__main__':
    if __name__ == '__main__':
        G = nx.Graph()

        G.add_nodes_from([
            (1, {'prize': 8}),
            (2, {'prize': 0}),
            (3, {'prize': 0}),
            (4, {'prize': 6}),
            (5, {'prize': 0}),
            (6, {'prize': 10})

        ])

        G.add_edges_from([(1, 2, {'weight': 2}), (1, 4, {'weight': 5}), (2, 4, {'weight': 1}),
                          (3, 4, {'weight': 1}), (4, 5, {'weight': 9}), (3, 6, {'weight': 4})])

        root = -1
        G, forced_terminals, sum_of_profits, root = pu.pcst_to_rpcst(G)
        for t in forced_terminals:
            G.nodes[t]['prize'] = 1000000000


        vor.reductionTechniques(G, root)
        print(G.edges)
        for t in forced_terminals:
            G.nodes[t]['prize'] = 0
        G = nx.to_undirected(G)
        optG = imp_nx.read(G)
        m = pl.create_model(optG, forced_terminals=forced_terminals, weight='weight')
        m.optimize()
        best_val = m.objVal
        solution = stp.extract_solution(optG, m)
        time_end = time.time()


        result = 0
        res_nodes = set()
        for (u, v) in solution:
            result += G.get_edge_data(u, v)['weight']
            res_nodes.add(u)
            res_nodes.add(v)
        for u in G.nodes():
            if u not in res_nodes:
                result += G.nodes[u]['prize']
        result -= len(forced_terminals) * sum_of_profits
        print(result)
        print(solution)