from exception import NoSeatAvailableError, SeatAlreadyTakenError
from database import Database
from audit_log import AuditLog

class SeatManager:
    def __init__(self):
        self.db = Database()
        self.audit_log = AuditLog()

    def get_available_seats(self, trip_id):
        
        query = """
            SELECT available_seats 
            FROM trip
            WHERE id = %s
        """
        result = self.db.execute_select(query, (trip_id,))
        return result[0][0] if result else 0

    def reserve_seat(self, trip_id, user_id, seat_number=None):
        
        try:
            self.cancel_expired_reservations(trip_id)
           
            available_seats = self.get_available_seats(trip_id)
            if available_seats <= 0:
                raise NoSeatAvailableError()
            
            
            if not seat_number:
                seat_number = self.find_available_seat(trip_id)
            
            
            if self.is_seat_taken(trip_id, seat_number):
                raise SeatAlreadyTakenError()
            
            trip_query = "SELECT cost FROM trip WHERE id = %s"
            trip_result = self.db.execute_select(trip_query, (trip_id,))
            if not trip_result:
                raise Exception("Trip not found")
            
            trip_cost = trip_result[0][0]
            
            ticket_query = """
                INSERT INTO ticket (user_id, trip_id, seat_number, price, status) 
                VALUES (%s, %s, %s, %s, 'RESERVED')
            """
            ticket_success = self.db.execute_query(ticket_query, (user_id, trip_id, seat_number, trip_cost))
            
            if not ticket_success:
                raise Exception("Failed to create reserved ticket")
            
           
            update_query = """
                UPDATE trip
                SET available_seats = available_seats - 1 
                WHERE id = %s AND available_seats > 0
            """
            success = self.db.execute_query(update_query, (trip_id,))
            
                      
            if not success:
                raise NoSeatAvailableError()
            
            return seat_number
                       
        except Exception as e:
            raise e
    
    def cancel_expired_reservations(self, trip_id):
        try:
            query = """
                SELECT tk.id, tk.user_id, tk.price, u.username , tr.start_time
                FROM ticket tk
                JOIN trip t ON tk.trip_id = t.id
                JOIN users u ON tk.user_id = u.id
                WHERE tk.trip_id = %s 
                AND tk.status = 'RESERVED'
                AND t.start_time <= NOW() + INTERVAL '24 hours'
                AND t.start_time > NOW()
            """ 
            expired_tickets = self.db.execute_select(query, (trip_id,)) 
        
            print(f"founded reserves: {len(expired_tickets) if expired_tickets else 0}")
        
            if not expired_tickets:  
                print("can not find expire reserve")
                return True
            
            cancelled_count = 0
            for ticket in expired_tickets:
                ticket_id, user_id, price, username = ticket  
                print(f"{ticket_id} canceled for {username}")
            
            
                update_seat_query = """
                    UPDATE trip
                    SET available_seats = available_seats + 1 
                    WHERE id = %s 
                """
                seat_success = self.db.execute_query(update_seat_query, (trip_id,))
            
          
                update_ticket_query = """
                    UPDATE ticket 
                    SET status = 'CANCELLED', cancelled_at = NOW() 
                    WHERE ticket_id = %s
                """
                ticket_success = self.db.execute_query(update_ticket_query, (ticket_id,))
            
                if seat_success and ticket_success:
                    cancelled_count += 1
                    self.audit_log.log_activity("system", f"auto_cancel_expired_reservation_{ticket_id}")
                    print(f"{ticket_id} canceled")
                else:
                    print(f"error in canceling {ticket_id}")
        
            print(f"{cancelled_count} canceled")
            return cancelled_count > 0
                        
        except Exception as e:
            print(f"error in canceling reserve {e}")
            return False
        
        
    def find_available_seat(self, trip_id):
        self.cancel_expired_reservations(trip_id)
        
        query = """
            SELECT COALESCE(MAX(seat_number), 0) + 1 
            FROM ticket
            WHERE trip_id = %s AND status != 'RESERVED' 
        """
        result = self.db.execute_select(query, (trip_id,))
        return result[0][0] if result else 1

    def is_seat_taken(self, trip_id, seat_number):
        self.cancel_expired_reservations(trip_id)
        
        query = """
            SELECT id FROM ticket
            WHERE trip_id = %s AND seat_number = %s AND status = 'RESERVED'
        """
        result = self.db.execute_select(query, (trip_id, seat_number))
        return bool(result)