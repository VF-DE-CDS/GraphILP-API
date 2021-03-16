class ILPSetSystem:        
    
    def setUniverse(self, U):        
        self.U = U
    
    def setSystem(self, S):        
        self.S = S
    
    def setIncMatrix(self, M):        
        self.M = M
    
    def setSystemVars(self, variables):        
        self.system_variables = variables            
    
    def setUniverseVars(self, variables):        
        self.universe_variables = variables
