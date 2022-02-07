
class Datum:

    def __init__(self, ticket, period, value):
        self.ticket = ticket
        self.period = period
        self.value = value
        self.flag = 0
        

    def __eq__(self, other):
        """Overrides the default implementation"""        
        if isinstance(other, Datum):
            return self.ticket == other.ticket and self.period == other.period  
        return False
