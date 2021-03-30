# +
from numpy import array, zeros
from graphilp.imports import ilpsetsystem as ilpss
from graphilp.covering.heuristics import setcover_greedy

S = ilpss.ILPSetSystem()

S.setSystem({1:{'weight':1}, 2:{'weight':1}, 3:{'weight':1}, 4:{'weight':1}, 5:{'weight':1}})
S.setUniverse({1:{'weight':1}, 2:{'weight':1}, 3:{'weight':1}, 4:{'weight':1}, 5:{'weight':1}, 6:{'weight':1}})
M = array([[1,1,1,0,0,0], [0,0,0,1,1,1], [1,1,0,0,0,0], [0,0,1,1,0,0], [0,0,0,0,1,1]])
S.setIncMatrix(M.transpose())

cover = setcover_greedy.getHeuristic(S)
set_vector = zeros(len(S.S))
for index, setname in enumerate(S.S):
    if setname in cover:
        set_vector[index] = 1
covered = sum(sum((S.M*set_vector).transpose())) >= len(S.U)

assert(covered == True)
