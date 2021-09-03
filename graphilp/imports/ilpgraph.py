class ILPGraph:
    """ Wrapper class for graph instances and variables of a related integer linear program
    """

    def set_nx_graph(self, G):
        """ Set the underlying NetworkX graph

        :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
        """
        self.G = G

    def set_edge_vars(self, variables):
        """ Set the dictionary of edge variables

        :param variables: a dictionary with variable names as keys and gurobipy variables as values
        """
        self.edge_variables = variables

    def set_node_vars(self, variables):
        """ Set the dictionary of node variables

        :param variables: a dictionary with variable names as keys and gurobipy variables as values
        """
        self.node_variables = variables

    def set_label_vars(self, variables):
        """ Set the dictionary of node label variables

        :param variables: a dictionary with variable names as keys and gurobipy variables as values
        """
        self.label_variables = variables
