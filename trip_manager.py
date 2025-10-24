from database import Database
from exception import BalanceError, TripClose, NoSeatAvailableError
from datetime import datetime , timedelta
from audit_log import AuditLog
from seat_manager import SeatManager



class TripManager:
    def __init__(self):
        self.db = Database()
        self.audit_log = AuditLog()
        self.seat_manager = SeatManager()
        
    def create_trip(self, cost, start_time, end_time , username = "admin"):
        query = """
            INSERT INTO trip (cost, start_time, end_time)  
            VALUES (%s, %s, %s)
        """
        result = self.db.execute_query(query, (cost, start_time, end_time))
        if result:
            self.audit_log.log_activity(username , "create_trip")
        return result

    def get_available_trips(self):
        query = """
            SELECT id, cost, start_time, end_time , available_seats
            FROM trip
            WHERE is_started = FALSE AND start_time > CURRENT_TIMESTAMP
            ORDER BY start_time
        """
        return self.db.execute_select(query)

    def get_trip(self, trip_id):
        query = "SELECT * FROM trip WHERE id = %s" 
        result = self.db.execute_select(query, (trip_id,))
        return result[0] if result else None

    def update_trip(self, trip_id, cost, start_time, end_time , username = "admin"):
        query = """
            UPDATE trip
            SET cost = %s, start_time = %s, end_time = %s 
            WHERE id = %s
        """
        result = self.db.execute_query(query, (cost, start_time, end_time, trip_id))
        if result:
            self.audit_log.log_activity(username , "update_trip")
        return result

    def delete_trip(self, trip_id , username = "admin"):
        query = "DELETE FROM trip WHERE id = %s"  
        result = self.db.execute_query(query, (trip_id,))
        if result:
            self.audit_log.log_activity(username , "delete_trip")
        return result

    def start_trip(self, trip_id):
        query = "UPDATE trip SET is_started = TRUE WHERE id = %s" 
        return self.db.execute_query(query, (trip_id,))
    
    def reserve_ticket(self, user_id, trip_id, username):
        trip = self.get_trip(trip_id)
        if not trip:
            return False
        
        if trip[4]:  # if trip["is_started"]
            raise TripClose()

        try:
            seat_number = self.seat_manager.reserve_seat(trip_id, user_id)
                        
            if seat_number:
                self.audit_log.log_activity(username, "reserve_ticket")
                return True
            else:
                return False
            
        except NoSeatAvailableError as e:
            raise e
        except Exception as e:
            print(f"Error in reserve_ticket: {e}")
            return False
        
    def check_and_cancel_expired_reservations(self, trip_id=None):
    
        try:
            if trip_id:
            
                self.seat_manager.cancel_expired_reservations(trip_id)
            else:
           
                trips = self.db.execute_select("SELECT id FROM trip WHERE start_time > NOW()")
                if trips is None:
                    return
                for trip in trips:
                    self.seat_manager.cancel_expired_reservations(trip[0])
                
        except Exception as e:
            print(f"Error cancel_expired_reservations: {e}")

    def purchase_ticket(self, user_id, trip_id , username):
        trip = self.get_trip(trip_id)
        if not trip:
            return False
        
        if trip[4]:  # if trip["is_started"]
            raise TripClose()
                   
        
        user_balance = self.get_user_balance(user_id)
        trip_cost = float(trip[1])
        
        if user_balance < trip_cost:
            raise BalanceError() 
        
        reserved_ticket = self.get_user_reserved_ticket(user_id, trip_id)
        return self.process_payment(user_id, trip_id, trip_cost, username, reserved_ticket) 
    
    
    def process_payment(self, user_id, trip_id, trip_cost, username, reserved_ticket=None):
        
        try:
            if reserved_ticket:
                ticket_id, seat_number, price = reserved_ticket
                
                
                success1 = self.db.execute_query(
                    "UPDATE users SET balance = balance - %s WHERE id = %s",
                    (trip_cost, user_id)
                )
                
                
                success2 = self.db.execute_query(
                    "UPDATE ticket SET status = 'PAID', price = %s WHERE id = %s AND user_id = %s",
                    (trip_cost, ticket_id, user_id)
                )
                            
                
                success3 = self.db.execute_query(
                    "INSERT INTO transactions (user_id, amount, type, description) VALUES (%s, %s, %s, %s)",
                    (user_id, -trip_cost, 'PURCHASE', f'Purchase reserved ticket {ticket_id}')
                )
                
                if success1 and success2 and success3:
                    self.audit_log.log_activity(username, "purchase_reserved_ticket")
                    return True
                
            else:
                seat_number = self.seat_manager.reserve_seat(trip_id, user_id)
                
                success1 = self.db.execute_query(
                    "UPDATE users SET balance = balance - %s WHERE id = %s",
                    (trip_cost, user_id)
                )
                
                
                success2 = self.db.execute_query(
                    "INSERT INTO ticket (user_id, trip_id, seat_number, price, status) VALUES (%s, %s, %s, %s, 'PAID')",  
                    (user_id, trip_id, seat_number, trip_cost)
                )
                            
                
                success3 = self.db.execute_query(
                    "INSERT INTO transactions (user_id, amount, type, description) VALUES (%s, %s, %s, %s)",
                    (user_id, -trip_cost, 'PURCHASE', f'Purchase ticket for trip {trip_id}')
                )
                
                if success1 and success2 and success3:
                    self.audit_log.log_activity(username, "purchase_new_ticket")
                    return True
            
            return False
            
        except NoSeatAvailableError as e:
            raise e
        except Exception as e:
            print(f"Error in process_payment: {e}")
            return False
       
        
    def get_user_reserved_ticket(self, user_id, trip_id):
        query = """
            SELECT id, seat_number, price
            FROM ticket 
            WHERE user_id = %s AND trip_id = %s AND status = 'RESERVED'
        """
        result = self.db.execute_select(query, (user_id, trip_id))
        return result[0] if result else None


    def get_user_balance(self, user_id):
        query = "SELECT balance FROM users WHERE id = %s"
        result = self.db.execute_select(query, (user_id,))
        return float(result[0][0]) if result else 0.0

    def increase_balance(self, user_id , amount , username):
        query = "UPDATE users SET balance = balance + %s WHERE id = %s"
        result = self.db.execute_query(query, (amount, user_id))
        
        if result:
            self.db.execute_query(
                "INSERT INTO transactions (user_id, amount, type, description) VALUES (%s, %s, %s, %s)",
                (user_id, amount, 'DEPOSIT', 'Increase balance')
            )
            self.audit_log.log_activity(username , "increase_balance")
            
        return result

    def get_user_tickets(self, user_id):
        query = """
            SELECT t.id, tr.cost, tr.start_time, tr.end_time, t.purchase_time , t.seat_number , t.status
            FROM ticket t  
            JOIN trip tr ON t.trip_id = tr.id  
            WHERE t.user_id = %s
            ORDER BY t.purchase_time DESC
        """
        result = self.db.execute_select(query, (user_id,))
        return result

    def get_all_users(self):
        query = "SELECT id, username, balance, created_at FROM users ORDER BY created_at DESC"
        result = self.db.execute_select(query)
        return result if result else []