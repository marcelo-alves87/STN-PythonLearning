
class Datum:

    def __init__(self, ticket):
        self.ticket = ticket        
        self.flag = False 
        

    def __eq__(self, other):
        """Overrides the default implementation"""        
        if isinstance(other, Datum):
            return self.ticket == other.ticket  
        return False
