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
SetCover.set_system(sets)
SetCover.set_inc_matrix(cover_matrix)
SetCover.set_universe(universe)
m = sc.create_model(SetCover)
m.optimize()

assert(m.objVal == 7)
