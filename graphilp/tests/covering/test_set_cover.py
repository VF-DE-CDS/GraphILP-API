# +
from numpy import array
from graphilp.imports import ilpsetsystem as ilpss
from graphilp.covering import set_cover as sc

cover_matrix = array(
      [[ 0.,  0.,   1],
       [ 1,  0.,  0.],
       [ 0.,  1,  0.],
       [ 1., 0., 0. ]])

#A = sp.csr_matrix(cover_matrix)
sets = {0:{'weight': 4},1:{'weight': 2},2:{'weight': 1}}
universe = [0, 1, 2, 3]
SetCover = ilpss.ILPSetSystem()
SetCover.setSystem(sets)
SetCover.setIncMatrix(cover_matrix)
SetCover.setUniverse(universe)
m = sc.createModel(SetCover)
m.optimize()

assert(m.objVal == 7)
