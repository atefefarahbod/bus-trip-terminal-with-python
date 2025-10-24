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
        
class NoSeatAvailableError(Exception):
    def __init__(self, message="capacity full"):
        self.message = message
        super().__init__(self.message)

class SeatAlreadyTakenError(Exception):
    def __init__(self, message="already taken"):
        self.message = message
        super().__init__(self.message)

class CancelTimePassedError(Exception):
    def __init__(self, message="time passed for cancel"):
        self.message = message
        super().__init__(self.message)