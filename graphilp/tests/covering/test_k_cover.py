# +
import numpy as np
import scipy.sparse as sp
from graphilp.imports import ilpsetsystem as ilpss
from graphilp.covering import k_cover as kc

cover_matrix = np.array([[ 0.,  0.,   1, 1],
           [ 1,  0.,  0., 1],
        [ 0.,  1,  1, 1],
        [ 0., 1, 1, 0],
        [ 1, 1, 0, 0]])

A = sp.csr_matrix(cover_matrix)
sets = {0:{'weight': 4},1:{'weight': 2},2:{'weight': 1}, 3:{'weight':3}}
universe = {0:{'weight': 4},1:{'weight': 2},2:{'weight': 1}, 3:{'weight':3}, 4:{'weight': 1}}
SetCover = ilpss.ILPSetSystem()
SetCover.setSystem(sets)
SetCover.setIncMatrix(A)
SetCover.setUniverse(universe )
m = kc.createModel(SetCover, 1)
m.optimize()

assert(m.objVal == 8)
# -


