from authentication import Authentication  
from trip_manager import TripManager
from ticket_manager import TicketManager
from seat_manager import SeatManager
from report_generator import ReportGenerator
from exception import BalanceError, TripClose, NoSeatAvailableError, CancelTimePassedError
import os
from datetime import datetime

class CLI:
    def __init__(self):
        self.authentication = Authentication()
        self.trip_manager = TripManager()
        self.ticket_manager = TicketManager()
        self.seat_manager = SeatManager()
        self.report_generator = ReportGenerator()
        self.is_superuser = False

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_main_menu(self):
        while True:
            self.clear_screen()
            print("Terminal System")
            print("1. Register")
            print("2. Login")
            print("3. Admin Login")
            print("4. View Available Trips")
            print("5. Exit")
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.register_user()
            elif choice == '2':
                self.login_user()
            elif choice == '3':
                self.login_admin()
            elif choice == '4':
                self.show_available_trips()
            elif choice == '5':
                print("Exiting...")
                break
            else:
                input("Invalid option. Press enter to continue")

    def register_user(self):
        self.clear_screen()
        print("Register New User")
        username = input("Username: ")
        password = input("Password: ")
        
        if self.authentication.register(username, password):
            print("Registration successful")
        else:
            print("Registration failed")
        input("Press enter")

    def login_user(self):
        self.clear_screen()
        print("User Login")
        username = input("Username: ")
        password = input("Password: ")
        
        if self.authentication.login(username, password):
            print(f"Welcome {username}!")
            self.user_dashboard()
        else:
            print("Invalid username or password")
            input("Press enter")

    def login_admin(self):
        self.clear_screen()
        print("Admin Login")
        username = input("Username: ")
        password = input("Password: ")
        
        if self.authentication.is_superuser(username, password):
            self.is_superuser = True
            print("Admin login successful")
            self.admin_dashboard()
        else:
            print("Invalid admin credentials")
            input("Press enter")

    def show_available_trips(self):
        self.clear_screen()
        print("Available Trips")
        
        trips = self.trip_manager.get_available_trips()
        if not trips:
            print("No available trips")
        else:
            for trip in trips:
                print(f"Trip ID: {trip[0]}")
                print(f"Cost: {trip[1]}")
                print(f"Start: {trip[2]}")
                print(f"End: {trip[3]}")
                print(f"Available Seats: {trip[4]}")
                print("-" * 40)
        
        input("Press enter")
        
    def check_expired_reservations_for_user(self):
    
        if not self.authentication.current_user:
            return
    
        try:
            user_id = self.authentication.current_user['id']
            username = self.authentication.current_user['username']
        
            cancelled_count = self.seat_manager.check_and_cancel_user_expired_reservations(user_id, username)
        
            if cancelled_count > 0:
                print(f"Auto-cancelled {cancelled_count} reservation(s) - trip starts within 24 hours")
                print("These reservations were automatically cancelled")
                input("Press enter to continue...")
                
        except Exception as e:
            print(f"Error checking near-trip reservations: {e}")
    
    def get_user_reserved_tickets(self):
        if not self.authentication.current_user:
            return []
    
        try:
            query = """
                SELECT t.id, tr.id, t.price, tr.start_time, t.seat_number
                FROM ticket t
                JOIN trip tr ON t.trip_id = tr.id
                WHERE t.user_id = %s
                AND t.status = 'RESERVED'
                AND tr.start_time > NOW()
                ORDER BY tr.start_time
            """
            return self.authentication.db.execute_select(query, (self.authentication.current_user['id'],))
        except Exception as e:
            print(f"Error getting reserved tickets: {e}")
            return []
        
    def convert_reservation_to_purchase(self, ticket_id):
        if not self.authentication.current_user:
            print("No user logged in")
            return False
    
        try:
            query = """
                UPDATE ticket 
                SET status = 'PAID', purchase_time = NOW()
                WHERE id = %s 
                AND status = 'RESERVED'
                AND user_id = %s
            """
            return self.authentication.db.execute_query(query, (ticket_id, self.authentication.current_user['id']))
        except Exception as e:
            print(f"Error converting reservation: {e}")
            return False

    def user_dashboard(self):
        if not self.authentication.current_user:
            print("Error: No user logged in")
            input("Press enter")
            return
        self.check_expired_reservations_for_user()
            
        while True:
            self.clear_screen()
            print(f"User Dashboard - {self.authentication.current_user['username']}")
            print(f"Balance: {self.authentication.current_user['balance']}")
            print("\n1. Increase Balance")
            print("2. Reserve Ticket")
            print("3. Purchase Ticket")
            print("4. Cancel Ticket")
            print("5. View My Tickets")
            print("6. Change Password")
            print("7. Logout")
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.increase_balance()
            elif choice == '2':
                self.reserve_ticket()
            elif choice == '3':
                self.purchase_ticket()
            elif choice == '4':
                self.cancel_ticket()
            elif choice == '5':
                self.view_my_tickets()
            elif choice == '6':
                self.change_password()
            elif choice == '7':
                self.authentication.current_user = None
                break
            else:
                input("Invalid option. Press enter to continue")

    def increase_balance(self):
        if not self.authentication.current_user:
            print("No user logged in")
            return
            
        self.clear_screen()
        print("Increase Balance")
        try:
            amount = float(input("Enter amount: "))
            if amount <= 0:
                print("Amount must be greater than zero")
            else:
                username = self.authentication.current_user['username']
                if self.trip_manager.increase_balance(self.authentication.current_user['id'], amount, username):
                    self.authentication.current_user['balance'] += amount
                    print("Balance increased successfully")
                else:
                    print("Error increasing balance")
        except ValueError:
            print("Invalid amount")
        input("Press enter")

    def reserve_ticket(self):
        if not self.authentication.current_user:
            print("No user logged in")
            input("Press enter")
            return
            
        self.clear_screen()
        print("Reserve Ticket")
        
        trips = self.trip_manager.get_available_trips()
        if not trips:
            print("No available trips")
            input("Press enter")
            return
        
        for trip in trips:
            print(f"Trip ID: {trip[0]} | Cost: {trip[1]} | Start: {trip[2]} | Seats: {trip[4]}")
        
        try:
            trip_id = int(input("\nEnter trip ID: "))
            
            trip = self.trip_manager.get_trip(trip_id)
            if not trip:
                print("Trip not found")
            else:
                try:
                    username = self.authentication.current_user['username']
                    if self.trip_manager.reserve_ticket(self.authentication.current_user['id'], trip_id, username):
                        print("Ticket reserved successfully")
                    else:
                        print("Error reserving ticket")
                except TripClose as e:
                    print(f"{e.message}")
                except NoSeatAvailableError as e:
                    print(f"{e.message}")
                    
        except ValueError:
            print("Invalid trip ID")
        
            input("Press enter")

    def purchase_ticket(self):
        if not self.authentication.current_user:
            print("No user logged in")
            input("Press enter")
            return
            
        self.clear_screen()
        print("Purchase Ticket")
        
        trips = self.trip_manager.get_available_trips()
        if not trips:
            print("No available trips")
            input("Press enter")
            return
        
        for trip in trips:
            print(f"Trip ID: {trip[0]} | Cost: {trip[1]} | Start: {trip[2]} | Seats: {trip[4]}")
        
        try:
            trip_id = int(input("\nEnter trip ID: "))
            
            trip = self.trip_manager.get_trip(trip_id)
            if not trip:
                print("Trip not found")
            else:
                try:
                    username = self.authentication.current_user['username']
                    if self.trip_manager.purchase_ticket(self.authentication.current_user['id'], trip_id, username):
                        trip_cost = float(trip[1])
                        self.authentication.current_user['balance'] -= trip_cost
                        print("Ticket purchased successfully")
                    else:
                        print("Error purchasing ticket")
                except BalanceError as e:
                    print(f"{e.message}")
                except TripClose as e:
                    print(f"{e.message}")
                except NoSeatAvailableError as e:
                    print(f"{e.message}")
                    
        except ValueError:
            print("Invalid trip ID")
        
        input("Press enter")
        
    def cancel_ticket(self):
        if not self.authentication.current_user:
            print("No user logged in")
            input("Press enter")
            return
        
        self.clear_screen()
        print("Cancel Ticket")
        
        tickets = self.trip_manager.get_user_tickets(self.authentication.current_user['id'])
        if not tickets:
            print("No tickets to cancel")
            input("Press enter")
            return
        
        print("Your tickets:")
        for ticket in tickets:
            print(f"Ticket ID: {ticket[0]} | Cost: {ticket[1]} | Start: {ticket[2]} | Seat: {ticket[5]} | Status: {ticket[6]}")
        
        try:
            ticket_id = int(input("\nEnter ticket ID to cancel: "))
            ticket_to_cancel = next((t for t in tickets if t[0] == ticket_id), None)
            if not ticket_to_cancel:
                print("Ticket not found")
                input("Press enter")
                return
            
            try:
                username = self.authentication.current_user['username']
                if self.ticket_manager.cancel_ticket(ticket_id, self.authentication.current_user['id'], username):
                    if ticket_to_cancel[6] == 'PAID':
                        refund_amount = float(ticket_to_cancel[1]) * 0.8
                        self.authentication.current_user['balance'] += refund_amount
                        print("Ticket cancelled successfully! 80% refund added to your balance.")
                    else:
                        print("Ticket cancelled successfully! (No refund for reserved tickets)")
                else:
                    print("Error cancelling ticket")
            except CancelTimePassedError as e:
                print(f"{e.message}")
            
        except ValueError:
            print("Invalid ticket ID")
    
        input("Press enter")
                    

    def view_my_tickets(self):
        if not self.authentication.current_user:
            print("No user logged in")
            input("Press enter")
            return
                
        self.check_expired_reservations_for_user()
            
        self.clear_screen()
        print("My Tickets")
        print("Your Reserved Tickets:")
        reserved_tickets = self.get_user_reserved_tickets()
        if reserved_tickets:
            for ticket in reserved_tickets:
                print(f"Ticket ID: {ticket[0]} | Trip: {ticket[1]} | Cost: {ticket[2]} | Start: {ticket[3]} | Seat: {ticket[4]}")
            print("-" * 50)
        else:
            print("No reserved tickets found")
            print("-" * 40)
            
        trips = self.trip_manager.get_available_trips()
        if not trips:
            print("No available trips")
            input("Press enter")
            return
    
        print("\nAvailable Trips:")
        for trip in trips:
            print(f"Trip ID: {trip[0]} | Cost: {trip[1]} | Start: {trip[2]} | Seats: {trip[4]}")
    
        print("\nOptions:")
        print("1. Purchase a new ticket")
        print("2. Purchase from reserved tickets")
    
        choice = input("\nEnter your choice (1 or 2): ")
    
        if choice == '1':
        
            try:
                trip_id = int(input("\nEnter trip ID: "))
            
                trip = self.trip_manager.get_trip(trip_id)
                if not trip:
                    print("Trip not found")
                else:
                    try:
                        username = self.authentication.current_user['username']
                        if self.trip_manager.purchase_ticket(self.authentication.current_user['id'], trip_id, username):
                            trip_cost = float(trip[1])
                            self.authentication.current_user['balance'] -= trip_cost
                            print("Ticket purchased successfully")
                        else:
                            print("Error purchasing ticket")
                    except BalanceError as e:
                        print(f"{e.message}")
                    except TripClose as e:
                        print(f"{e.message}")
                    except NoSeatAvailableError as e:
                        print(f"{e.message}")
                    
            except ValueError:
                print("Invalid trip ID")
    
        elif choice == '2':
        
            if not reserved_tickets:
                print("You have no reserved tickets to purchase")
            else:
                try:
                    ticket_id = int(input("\nEnter reserved ticket ID to purchase: "))
                
                
                    reserved_ticket = next((t for t in reserved_tickets if t[0] == ticket_id), None)
                    if not reserved_ticket:
                        print("Reserved ticket not found")
                    else:
                    
                        if self.convert_reservation_to_purchase(ticket_id):
                            trip_cost = float(reserved_ticket[2])
                            self.authentication.current_user['balance'] -= trip_cost
                            print("Reserved ticket purchased successfully!")
                        else:
                            print("Error purchasing reserved ticket")
                        
                except ValueError:
                    print("Invalid ticket ID")
        else:
            print("Invalid choice")
    
            input("Press enter")
        
                
    def change_password(self):
        if not self.authentication.current_user:
            print("No user logged in")
            input("Press enter")
            return
            
        self.clear_screen()
        print("Change Password")
        new_password = input("New password: ")
        
        if self.authentication.change_password(new_password):
            print("Password changed successfully")
        else:
            print("Error changing password")
        
        input("Press enter")

    def admin_dashboard(self):
        while True:
            self.clear_screen()
            print("Admin Panel")
            print("1. Manage Trips")
            print("2. View All Users")
            print("3. View Reports")
            print("4. View Audit Logs")
            print("5. System Statistics")
            print("6. Logout")
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.manage_trips()
            elif choice == '2':
                self.show_all_users()
            elif choice == '3':
                self.view_reports()
            elif choice == '4':
                self.view_audit_logs()
            elif choice == '5':
                self.system_statistics()
            elif choice == '6':
                self.is_superuser = False
                break
            else:
                input("Invalid option. Press enter to continue")

    def manage_trips(self):
        while True:
            self.clear_screen()
            print("Manage Trips")
            print("1. Add New Trip")
            print("2. View All Trips")
            print("3. Edit Trip")
            print("4. Delete Trip")
            print("5. Start Trip")
            print("6. Back")
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.add_trip()
            elif choice == '2':
                self.show_all_trips()
            elif choice == '3':
                self.edit_trip()
            elif choice == '4':
                self.delete_trip()
            elif choice == '5':
                self.start_trip()
            elif choice == '6':
                break
            else:
                input("Invalid option. Press enter to continue")

    def add_trip(self):
        self.clear_screen()
        print("Add New Trip")
        try:
            cost = float(input("Trip cost: "))
            start_time = input("Start time (YYYY-MM-DD HH:MM:SS): ")
            end_time = input("End time (YYYY-MM-DD HH:MM:SS): ")
            
            if not self._validate_date(start_time) or not self._validate_date(end_time):
                print("Invalid date format")
                input("Press enter")
                return
            
            if self.trip_manager.create_trip(cost, start_time, end_time):
                print("Trip added successfully")
            else:
                print("Error adding trip")
        except ValueError:
            print("Invalid value")
        input("Press enter")

    def _validate_date(self, date_string):
        try:
            datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            return True
        except ValueError:
            return False

    def show_all_trips(self):
        self.clear_screen()
        print("All Trips")
        
        trips = self.trip_manager.db.execute_select("SELECT id, cost, start_time, end_time, is_started, capacity, available_seats FROM trip ORDER BY start_time")
        
        if not trips:
            print("No trips found")
        else:
            for trip in trips:
                status = "Started" if trip[4] else "Waiting"
                print(f"Trip ID: {trip[0]}")
                print(f"Cost: {trip[1]}")
                print(f"Start: {trip[2]}")
                print(f"End: {trip[3]}")
                print(f"Status: {status}")
                print(f"Capacity: {trip[5]}, Available: {trip[6]}")
                print("-" * 40)
        
        input("Press enter")

    def show_all_users(self):
        self.clear_screen()
        print("All Users")
        
        users = self.trip_manager.get_all_users()
        if not users:
            print("No users found")
        else:
            for user in users:
                print(f"User ID: {user[0]}")
                print(f"Username: {user[1]}")
                print(f"Balance: {user[2]}")
                print(f"Registered: {user[3]}")
                print("-" * 40)
        
        input("Press enter")

    def view_audit_logs(self):
        self.clear_screen()
        print("Audit Logs")
        
        logs = self.authentication.db.execute_select("SELECT username, action, created_at FROM audit_log ORDER BY created_at DESC LIMIT 20")
        
        if not logs:
            print("No audit logs found")
        else:
            print(f"{'User':<15} {'Action':<25} {'Time':<20}")
            print("-" * 60)
            for log in logs:
                print(f"{log[0]:<15} {log[1]:<25} {log[2]:<20}")
        
        input("Press enter")

    def view_reports(self):
        self.clear_screen()
        print("Reports")
        print("1. Total Revenue")
        print("2. Trip Revenue")
        print("3. Daily Report")
        print("4. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == '1':
            self.show_total_revenue()
        elif choice == '2':
            self.show_trip_revenue()
        elif choice == '3':
            self.show_daily_report()
        elif choice == '4':
            return
        else:
            input("Invalid option. Press enter to continue")

    def show_total_revenue(self):
        self.clear_screen()
        print("Total Revenue")
        total_revenue = self.report_generator.get_total_revenue()
        print(f"Total Revenue: {total_revenue}")
        input("Press enter")

    def show_trip_revenue(self):
        self.clear_screen()
        print("Trip Revenue")
        trip_id = input("Enter trip ID: ")
        if trip_id.isdigit():
            revenue = self.report_generator.get_trip_revenue(int(trip_id))
            print(f"Revenue for trip {trip_id}: {revenue}")
        else:
            print("Invalid trip ID")
        input("Press enter")

    def show_daily_report(self):
        self.clear_screen()
        print("Daily Report")
        date = input("Enter date (YYYY-MM-DD) or press enter for today: ")
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        report = self.report_generator.get_daily_report(date)
        if report:
            tickets_sold, daily_income, cancelled_count = report[0]
            print(f"Date: {date}")
            print(f"Tickets Sold: {tickets_sold}")
            print(f"Daily Income: {daily_income}")
            print(f"Cancelled Tickets: {cancelled_count}")
        else:
            print("No data for this date")
        input("Press enter")

    def system_statistics(self):
        self.clear_screen()
        print("System Statistics")
        
        users = self.trip_manager.get_all_users()
        users_count = len(users) if users else 0
        
        trips_result = self.authentication.db.execute_select("SELECT COUNT(*) FROM trip")
        trips_count = trips_result[0][0] if trips_result else 0
        
        tickets_result = self.authentication.db.execute_select("SELECT COUNT(*) FROM ticket")
        tickets_count = tickets_result[0][0] if tickets_result else 0
        
        total_revenue = self.report_generator.get_total_revenue()
        
        print(f"Total Users: {users_count}")
        print(f"Total Trips: {trips_count}")
        print(f"Total Tickets: {tickets_count}")
        print(f"Total Revenue: {total_revenue}")
        
        input("Press enter")

    def edit_trip(self):
        self.clear_screen()
        print("Edit Trip")
        
        trip_id = input("Enter trip ID: ")
        if not trip_id.isdigit():
            print("Invalid trip ID")
            input("Press enter")
            return
        
        trip = self.trip_manager.get_trip(int(trip_id))
        if not trip:
            print("Trip not found")
            input("Press enter")
            return
        
        try:
            cost = float(input(f"New cost [{trip[1]}]: ") or trip[1])
            start_time = input(f"New start time [{trip[2]}]: ") or trip[2]
            end_time = input(f"New end time [{trip[3]}]: ") or trip[3]
            
            if self.trip_manager.update_trip(int(trip_id), cost, start_time, end_time):
                print("Trip updated successfully")
            else:
                print("Error updating trip")
        except ValueError:
            print("Invalid value")
        input("Press enter")

    def delete_trip(self):
        self.clear_screen()
        print("Delete Trip")
        
        trip_id = input("Enter trip ID: ")
        if not trip_id.isdigit():
            print("Invalid trip ID")
            input("Press enter")
            return
        
        confirm = input("Are you sure you want to delete this trip? (y/n): ")
        if confirm.lower() == 'y':
            if self.trip_manager.delete_trip(int(trip_id)):
                print("Trip deleted successfully")
            else:
                print("Error deleting trip")
        
        input("Press enter")

    def start_trip(self):
        self.clear_screen()
        print("Start Trip")
        
        trip_id = input("Enter trip ID: ")
        if not trip_id.isdigit():
            print("Invalid trip ID")
            input("Press enter")
            return
        
        if self.trip_manager.start_trip(int(trip_id)):
            print("Trip started successfully")
        else:
            print("Error starting trip")
        
        input("Press enter")
    
    

    

if __name__ == "__main__":
    cli = CLI()
    cli.show_main_menu()