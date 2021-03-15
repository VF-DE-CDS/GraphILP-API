import networkx as nx

class ILPGraph:
    """ Wrapper class for graph instances and variables of a related integer linear program
    """
    
    def setNXGraph(self, G):
        """ set the underlying NetworkX graph
        """
        self.G = G
        
    def setEdgeVars(self, variables):
        """ set the dictionary of edge variables
        
        :param variables: a dictionary with variable names as keys and gurobipy variables as values
        """
        self.edge_variables = variables
        
    def setNodeVars(self, variables):
        """ set the dictionary of node variables
        
        :param variables: a dictionary with variable names as keys and gurobipy variables as values
        """
        self.node_variables = variables

    def setLabelVars(self, variables):
        """ set the dictionary of node label variables
        
        :param variables: a dictionary with variable names as keys and gurobipy variables as values
        """
        self.label_variables = variables
    
    def setFlowVars(self, variables):
        self.flow_variables = variables
