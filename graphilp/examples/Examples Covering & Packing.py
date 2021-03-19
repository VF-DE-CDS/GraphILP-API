# +
import sys, os
sys.path.append(os.path.abspath('..'))
import numpy as np
import scipy.sparse as sp
from imports import ilpsetsystem as ilpss
from covering import set_cover as sc
from imports import readFile

path ="/home/tsauter/GraphILP/GraphILP-API/graphilp/examples/setcoverTestInstances/scpd1.txt"
cover_matrix, sets = readFile.read_set_cover(path)
A = sp.csr_matrix(cover_matrix)
universe = [i for i in range(400)]
SetCover = ilpss.ILPSetSystem()
SetCover.setSystem(sets)
SetCover.setIncMatrix(A)
SetCover.setUniverse(universe )
m = sc.createModel(SetCover, A)
m.optimize()
# -

# # Optimal solution k - coverage

# +
import sys, os
sys.path.append(os.path.abspath('..'))
import numpy as np
import scipy.sparse as sp
from imports import ilpsetsystem as ilpss
from covering import k_cover as kc
from imports import readFile
import random

path ="/home/tsauter/GraphILP/GraphILP-API/graphilp/examples/setcoverTestInstances/scpd1.txt"
cover_matrix, sets = readFile.read_set_cover(path)
A = sp.csr_matrix(cover_matrix)
universe = {}
for i in range(len(cover_matrix)):
    universe[i] = {'weight':1}
SetCover = ilpss.ILPSetSystem()
SetCover.setSystem(sets)
SetCover.setIncMatrix(A)
SetCover.setUniverse(universe)
m = kc.createModel(SetCover, A, 20)
m.optimize()
# -

# # Set Packing Optimal solution

# +
import sys, os
sys.path.append(os.path.abspath('..'))
import numpy as np
import scipy.sparse as sp
from imports import ilpsetsystem as ilpss
from covering import set_packing as setp
from imports import readFile

path ="/home/tsauter/GraphILP/GraphILP-API/graphilp/examples/setcoverTestInstances/scpd1.txt"
cover_matrix, sets = readFile.read_set_cover(path)
A = sp.csr_matrix(cover_matrix)
universe = [i for i in range(400)]
SetCover = ilpss.ILPSetSystem()
SetCover.setSystem(sets)
SetCover.setIncMatrix(A)
SetCover.setUniverse(universe )
m = setp.createModel(SetCover, A)
m.Params.MIPGap = 0.25
m.optimize()
sol = m.getVars()
i = 0
for s in sol:
    if s.X > 0.5:
        i += 1

print("Number of included sets: ", i)
# -


