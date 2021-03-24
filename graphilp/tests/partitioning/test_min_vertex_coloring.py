import sys
sys.path.append("../..")

import networkx as nx
from graphilp.partitioning.min_vertex_coloring import *
from graphilp.imports import networkx as imp_nx

# +
# create an odd length cycle and an even length cycle
even_length = 12
odd_length  = 11

G_even_init = nx.cycle_graph(n=even_length)
G_odd_init = nx.cycle_graph(n=odd_length)

#create ILPGraph objects
G_even = imp_nx.read(G_even_init)
G_odd = imp_nx.read(G_odd_init)

m_even = createModel(G_even)
m_odd = createModel(G_odd)

# get colouring for even length cycle and check the number of colours
m_even.optimize()
color_assignment_even, node_to_col_even = extractSolution(G_even, m_even)
# even cylces can be coloured by two colours
assert(len(set(node_to_col_even.values())) == 2)

# get colouring for odd length cycle and check the number of colours
m_odd.optimize()
color_assignment_odd, node_to_col_odd = extractSolution(G_odd, m_odd)
# odd cylces need by three colours
assert(len(set(node_to_col_odd.values())) == 3)
