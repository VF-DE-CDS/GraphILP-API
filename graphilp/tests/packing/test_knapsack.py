# +
import numpy as np
import scipy.sparse as sp
from graphilp.imports import ilpsetsystem as ilpss
from graphilp.covering import knapsack as kp

weight_matrix = np.array([5,4,5])
A = sp.csr_matrix(weight_matrix)
sets = {0:{'weight': 4, 'value':5}, 1:{'weight': 2, 'value':4}, 2:{'weight': 1, 'value':3}}
universe = {0:{'weight': 4}, 1:{'weight': 2}, 2:{'weight': 1}}
SetCover = ilpss.ILPSetSystem()
SetCover.setSystem(sets)
SetCover.setIncMatrix(A)
SetCover.setUniverse(universe )
m = kp.createModel(SetCover, 5)
m.optimize()

assert(m.objVal == 5.0)
