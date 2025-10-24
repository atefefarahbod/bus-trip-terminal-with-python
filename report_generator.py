from database import Database
from datetime import datetime, timedelta

class ReportGenerator:
    def __init__(self):
        self.db = Database()

    def get_trip_revenue(self, trip_id): 
        
        query = """
            SELECT COALESCE(SUM(price), 0) 
            FROM ticket 
            WHERE trip_id = %s AND status = 'PAID'
        """
        result = self.db.execute_select(query, (trip_id,))
        return float(result[0][0]) if result else 0.0

    def get_total_revenue(self):
        
        query = """
            SELECT COALESCE(SUM(price), 0) 
            FROM ticket 
            WHERE status = 'PAID'
        """
        result = self.db.execute_select(query)
        return float(result[0][0]) if result else 0.0

    def get_trip_statistics(self, trip_id):
        
        query = """
            SELECT 
                COUNT(*) as total_tickets,
                COUNT(CASE WHEN status = 'PAID' THEN 1 END) as sold_tickets,
                COUNT(CASE WHEN status = 'CANCELLED' THEN 1 END) as cancelled_tickets
            FROM ticket 
            WHERE trip_id = %s
        """
        return self.db.execute_select(query, (trip_id,))

    def get_daily_report(self, date=None):
        
        if not date:
            date = datetime.now().date()
        
        query = """
            SELECT 
                COUNT(*) as tickets_sold,
                COALESCE(SUM(price), 0) as daily_income,
                COUNT(CASE WHEN status = 'CANCELLED' THEN 1 END) as cancelled_count
            FROM ticket 
            WHERE DATE(purchase_time) = %s
        """
        return self.db.execute_select(query, (date,))