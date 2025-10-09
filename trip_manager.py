from database import Database
from exception import BalanceError, TripClose
from datetime import datetime


class TripManager:
    def __init__(self):
        self.db = Database()

    def create_trip(self, cost, start_time, end_time):
        query = """
            INSERT INTO trip (cost, start_time, end_time)  
            VALUES (%s, %s, %s)
        """
        return self.db.execute_query(query, (cost, start_time, end_time))

    def get_available_trips(self):
        query = """
            SELECT id, cost, start_time, end_time 
            FROM trip
            WHERE is_started = FALSE AND start_time > CURRENT_TIMESTAMP
            ORDER BY start_time
        """
        return self.db.execute_select(query)

    def get_trip(self, trip_id):
        query = "SELECT * FROM trip WHERE id = %s" 
        result = self.db.execute_select(query, (trip_id,))
        return result[0] if result else None

    def update_trip(self, trip_id, cost, start_time, end_time):
        query = """
            UPDATE trip
            SET cost = %s, start_time = %s, end_time = %s 
            WHERE id = %s
        """
        return self.db.execute_query(query, (cost, start_time, end_time, trip_id))

    def delete_trip(self, trip_id):
        query = "DELETE FROM trip WHERE id = %s"  
        return self.db.execute_query(query, (trip_id,))

    def start_trip(self, trip_id):
        query = "UPDATE trip SET is_started = TRUE WHERE id = %s" 
        return self.db.execute_query(query, (trip_id,))

    def purchase_ticket(self, user_id, trip_id):
        trip = self.get_trip(trip_id)
        if not trip:
            return False
        
        if trip[4]:  # is_started
            raise TripClose() 
        
        user_balance = self.get_user_balance(user_id)
        trip_cost = float(trip[1])
        
        if user_balance < trip_cost:
            raise BalanceError()  

        try:
            success1 = self.db.execute_query(
                "UPDATE users SET balance = balance - %s WHERE id = %s",
                (trip_cost, user_id)
            )
            
            success2 = self.db.execute_query(
                "INSERT INTO ticket (user_id, trip_id, price) VALUES (%s, %s, %s)",  
                (user_id, trip_id, trip_cost)
            )
                        
            success3 = self.db.execute_query(
                "INSERT INTO transactions (user_id, amount, type, description) VALUES (%s, %s, %s, %s)",
                (user_id, -trip_cost, 'PURCHASE', f'Purchase ticket for trip {trip_id}')
            )
            
            return success1 and success2 and success3
            
        except Exception as e:
            print(f"Error in purchase_ticket: {e}")
            return False

    def get_user_balance(self, user_id):
        query = "SELECT balance FROM users WHERE id = %s"
        result = self.db.execute_select(query, (user_id,))
        return float(result[0][0]) if result else 0.0

    def increase_balance(self, user_id, amount):
        query = "UPDATE users SET balance = balance + %s WHERE id = %s"
        result = self.db.execute_query(query, (amount, user_id))
        
        if result:
            self.db.execute_query(
                "INSERT INTO transactions (user_id, amount, type, description) VALUES (%s, %s, %s, %s)",
                (user_id, amount, 'DEPOSIT', 'Increase balance')
            )
        return result

    def get_user_tickets(self, user_id):
        query = """
            SELECT t.id, tr.cost, tr.start_time, tr.end_time, t.purchase_time
            FROM ticket t  
            JOIN trip tr ON t.trip_id = tr.id  
            WHERE t.user_id = %s
            ORDER BY t.purchase_time DESC
        """
        return self.db.execute_select(query, (user_id,))

    def get_all_users(self):
        query = "SELECT id, username, balance, created_at FROM users ORDER BY created_at DESC"
        return self.db.execute_select(query)