
class Datum:

    def __init__(self, ticket):
        self.ticket = ticket
        #0 - None, 1 - Reset, 2 - Hit, 3 - Over
        self.flag = 0 
        

    def __eq__(self, other):
        """Overrides the default implementation"""        
        if isinstance(other, Datum):
            return self.ticket == other.ticket  
        return False
