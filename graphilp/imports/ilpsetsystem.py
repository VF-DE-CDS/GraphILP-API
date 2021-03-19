class ILPSetSystem:        
    """ Wrapper class for set systems (undirected hyper graphs)
    
    Joint representation of set system instances and variables of a related integer linear program
    """
    
    def setUniverse(self, U):  
        """ set the universe of the set system
        
        :param U: the universe of the set system
        """
        self.U = U
    
    def setSystem(self, S):  
        """ set the names of the sets in the system
        
        :param S: the system of the set system
        """
        self.S = S
    
    def setIncMatrix(self, M):    
        """ set the incidence matrix of the system
        
        The incidence matrix indicates which element of the universe is contained in which set of the system.
        
        :param M: the incidence matrix of the set system
        """
        self.M = M
    
    def setSystemVars(self, variables):  
        """ set the dictionary of indicator variables for the elements of the system
                
        :param variables: a dictionary with variable names as keys and gurobipy variables as values
        """
        self.system_variables = variables            
    
    def setUniverseVars(self, variables):      
        """ set the dictionary of indicator variables for elements of the universe

        :param variables: a dictionary with variable names as keys and gurobipy variables as values
        """
        self.universe_variables = variables
