from database import Database
import hashlib
import os

class Authentication:
    def __init__(self) -> None:
        self.db = Database()
        self.current_user = None
        
    def hash_password(self , password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password):
        hashed_password = self.hash_password(password)
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        return self.db.execute_query(query, (username, hashed_password))
    
    def login(self, username, password):
        hashed_password = self.hash_password(password)
        query = "SELECT id, username, balance FROM users WHERE username = %s AND password = %s"
        result = self.db.execute_select(query, (username, hashed_password))
        
        if result and len(result) > 0:
            self.current_user = {
                'id': result[0][0], 
                'username': result[0][1], 
                'balance': float(result[0][2])
            }
            return True
        return False
    
    def is_superuser(self, username, password):
        superuser_username = os.getenv('SUPERUSER_USERNAME')
        superuser_password = os.getenv('SUPERUSER_PASSWORD')
        return username == superuser_username and password == superuser_password
    
    def change_password(self, new_password):
        if not self.current_user:
            return False
        
        hashed_password = self.hash_password(new_password)
        query = "UPDATE users SET password = %s WHERE id = %s"
        return self.db.execute_query(query, (hashed_password, self.current_user['id']))
    
    