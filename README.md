GraphILP
========

GraphILP is a Python API to automatically cast graph-related optimisation problems into integer linear programming (ILP) instances.

* Source: https://github.com/VF-DE-CDS/GraphILP-API
* Documentation: TODO

Simple example
-------------------

Find the smallest number colours needed to colour the vertices of a cycle such that adjacent vertices have different colours.

```python
import networkx as nx

from graphilp.imports import networkx as imp_nx
from graphilp.partitioning import min_vertex_coloring as vtx

G_init = nx.cycle_graph(n=5)
G = imp_nx.read(G_init)

m = vtx.create_model(G)
m.optimize()

color_to_node, node_to_color = vtx.extract_solution(G, m)
```

Installation
-------------

Requirements: Networkx and Gurobi

Check out repository and add the path to your PYTHONPATH.
For example:

```bash
export PYTHONPATH=$PYTHONPATH:< your path >
```

Licence
---------

The GraphILP API is released under the MIT License. See LICENSE.txt for the details.