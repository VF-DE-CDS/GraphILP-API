import networkx as nx

class ILPGraph:
    
    def setNXGraph(self, G):
        self.G = G
        
    def setEdgeVars(self, variables):
        self.edge_variables = variables
        
    def setNodeVars(self, variables):
        self.node_variables = variables

    def setLabelVars(self, variables):
        self.label_variables = variables
