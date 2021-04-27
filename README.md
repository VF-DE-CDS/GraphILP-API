GraphILP
========

GraphILP is a Python API to automatically cast graph-related optimisation problems into integer linear programming (ILP) instances.

* **Source:** https://github.com/VF-DE-CDS/GraphILP-API
* **Documentation:** https://VF-DE-CDS.github.io/GraphILP-API-docs/

Simple example
--------------

Find the smallest number of colours needed to colour the vertices of a cycle such that adjacent vertices have different colours.

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

The best way to get started with GraphILP is through one of our examples.

Installation
------------

GraphILP has two main requirements: 

1. [NetworkX](https://networkx.org) is used internally to represent graphs. It is also the easiest way to create problem instances.
2. GraphILP creates integer linear programs in the form of [Gurobi](https://www.gurobi.com) models. To create and solve these models, you need the Gurobi solver and its [Python API](https://www.gurobi.com/documentation/9.1/quickstart_mac/cs_using_pip_to_install_gr.html).

Some additional libraries are required for running the examples.

While GraphILP is not yet on PyPI, it can be installed by checking out the repository and adding the path to your PYTHONPATH.
For example:

```bash
export PYTHONPATH=$PYTHONPATH:< your path >
```

Licence
-------

The GraphILP API is released under the MIT License. See LICENSE.txt for the details.

Authors
-------

### Core development team

* Rolf Bardeli <rolf.bardeli1@vodafone.com>
* Richard Schmied <richard.schmied@vodafone.com>
* Morris Stallmann <morris.stallmann1@vodafone.com>

### Contributors

* Adrian Prinz
* Thomas Sauter
