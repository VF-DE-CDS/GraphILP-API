# +
import networkx as nx
from graphilp.covering.set_cover import *
import scipy.sparse as sp
from graphilp.imports import networkx as imp_nx
from graphilp.imports import ilpsetsystem as ilpss
import numpy as np

cover_matrix = np.array(
      [[ 0.,  0.,   1],
       [ 1,  0.,  0.],
       [ 0.,  1,  0.],
       [ 1., 0., 0. ]])

A = sp.csr_matrix(cover_matrix)
sets = {0:{'weight': 4},1:{'weight': 2},2:{'weight': 1}}
universe = [0, 1, 2, 3]
SetCover = ilpss.ILPSetSystem()
SetCover.setSystem(sets)
SetCover.setIncMatrix(A)
SetCover.setUniverse(universe )
m = createModel(SetCover, A)
m.optimize()

assert(m.objVal == 7)
