class BalanceError(Exception):
    def __init__(self, message = "there is not enough balance"):
        self.message = message
        super().__init__(self.message)
    
class TripClose(Exception):
    def __init__(self, message = "trip is out of acces"):
        self.message = message
        super().__init__(self.message)
        
class UserNotFound(Exception):
    def __init__(self, message = "we have no such a user"):
        self.message = message
        super().__init__(self.message)