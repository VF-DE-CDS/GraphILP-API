# +
import numpy as np
import scipy.sparse as sp
from graphilp.imports import ilpsetsystem as ilpss
from graphilp.packing import set_packing as setp

cover_matrix = np.array([[ 0.,  0.,   1],
       [ 1,  0.,  0.],
       [ 0.,  1,  1]])
A = sp.csr_matrix(cover_matrix)
sets = {0:{'weight': 4},1:{'weight': 2},2:{'weight': 1}}
universe = [0, 1, 2]
SetCover = ilpss.ILPSetSystem()
SetCover.setSystem(sets)
SetCover.setIncMatrix(A)
SetCover.setUniverse(universe )
m = setp.createModel(SetCover, A)
m.optimize()


assert(m.objVal == 6.0)
