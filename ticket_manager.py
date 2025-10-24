from datetime import datetime, timedelta
from exception import CancelTimePassedError
from database import Database
from audit_log import AuditLog
from trip_manager import TripManager

class TicketManager:
    def __init__(self):
        self.db = Database()
        self.audit_logger = AuditLog()
        self.trip_manager = TripManager()

    def cancel_ticket(self, ticket_id, user_id, username):
        query = """
            SELECT t.start_time, tk.price, tk.user_id, tk.trip_id
            FROM ticket tk
            JOIN trip t ON tk.trip_id = t.id
            WHERE tk.id = %s
        """
        result = self.db.execute_select(query, (ticket_id,))
        
        if not result:
            return False
        
        start_time, price, ticket_user_id, trip_id = result[0]
        
      
        if ticket_user_id != user_id:
            return False
        
        
        if datetime.now() > start_time - timedelta(hours=2):
            raise CancelTimePassedError()
        
        price_float = float(price)
        refund_amount = price_float * 0.8
        
      
        update_query = """
            UPDATE ticket
            SET status = 'CANCELLED', cancelled_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        """
        success = self.db.execute_query(update_query, (ticket_id,))
        
        if success: 
           
            self.trip_manager.increase_balance(user_id, refund_amount, username)  
            
           
            self.free_seat(trip_id)
            
          
            self.audit_logger.log_activity(username, "PAYMENT_TICKET_REFUND")
            
            return True
        return False

    def free_seat(self, trip_id):
        query = """
            UPDATE trip
            SET available_seats = available_seats + 1 
            WHERE id = %s
        """
        return self.db.execute_query(query, (trip_id,))

    def get_user_tickets(self, user_id):
        query = """
            SELECT t.id, tr.cost, tr.start_time, tr.end_time, t.purchase_time, 
                   t.seat_number, t.status
            FROM ticket t
            JOIN trip tr ON t.trip_id = tr.id
            WHERE t.user_id = %s
            ORDER BY t.purchase_time DESC
        """
        return self.db.execute_select(query, (user_id,))