# +
from numpy import array
from graphilp.imports import ilpsetsystem as ilpss
from graphilp.covering.heuristics import setcover_greedy

S = ilpss.ILPSetSystem()

S.setSystem({1:{'weight':1}, 2:{'weight':1}, 3:{'weight':1}, 4:{'weight':1}, 5:{'weight':1}})
S.setUniverse({1:{'weight':1}, 2:{'weight':1}, 3:{'weight':1}, 4:{'weight':1}, 5:{'weight':1}, 6:{'weight':1}})
M = array([[1,1,1,0,0,0], [0,0,0,1,1,1], [1,1,0,0,0,0], [0,0,1,1,0,0], [0,0,0,0,1,1]])
S.setIncMatrix(M.transpose())

k = 2

cover = setcover_greedy.getHeuristic(S, k)

assert(len(cover) <= k)
