from database import Database

class AuditLog:
    def __init__(self) -> None:
        self.db = Database()
        
    def log_activity(self , username , action):
        
        query = """
            INSERT INTO audit_log (username , action)
            VALUES (%s , %s)
        """
        result = self.db.execute_query(query , (username , action))
        return result