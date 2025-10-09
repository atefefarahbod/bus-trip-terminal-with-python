from authentication import Authentication  
from trip_manager import TripManager
from exception import BalanceError, TripClose
import os
from datetime import datetime

class CLI:
    def __init__(self):
        self.authentication = Authentication()
        self.trip_manager = TripManager()
        self.is_superuser = False

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_main_menu(self):
        while True:
            self.clear_screen()
            print("terminal system")
            print("1. register ")
            print("2. login ")
            print("3. admin entrance ")
            print("4. view available trips")
            print("5. exit")
            
            choice = input("\nplease insert your option: ")
            
            if choice == '1':
                self.register_user()
            elif choice == '2':
                self.login_user()
            elif choice == '3':
                self.login_admin()
            elif choice == '4':
                self.show_available_trips()
            elif choice == '5':
                print("exit ...")
                break
            else:
                input("invalid option press enter to exit")

    def register_user(self):
        self.clear_screen()
        print("register new user")
        username = input("username: ")
        password = input("password : ")
        
        if self.authentication.register(username, password):
            print("register done successfully")
        else:
            print("error in register")
        input("press enter")

    def login_user(self):
        self.clear_screen()
        print("login user")
        username = input("username: ")
        password = input("password : ")
        
        if self.authentication.login(username, password):
            print(f"welcome {username}!")
            self.user_dashboard()
        else:
            print("wrong username or password")
            input("press enter")

    def login_admin(self):
        self.clear_screen()
        print("admin entrance")
        username = input("username: ")
        password = input("password : ")
        
        if self.authentication.is_superuser(username, password):
            self.is_superuser = True
            print("you entered successfully")
            self.admin_dashboard()
        else:
            print ("wrong info for admin")
            input("press enter")

    def show_available_trips(self):
        self.clear_screen()
        print("available trips")
        
        trips = self.trip_manager.get_available_trips()
        if not trips:
            print("there is no availble trip")
        else:
            for trip in trips:
                print(f"trip code  : {trip[0]}")
                print(f"cost : {trip[1]} ")
                print(f"trip started at : {trip[2]}")
                print(f"trip end at : {trip[3]}")
                print("-" * 40)
        
        input("press enter")

    def user_dashboard(self):
        if not self.authentication.current_user:
            print("Error: No user logged in")
            input("press enter")
            return
            
        while True:
            self.clear_screen()
            print(f"user dashbord - {self.authentication.current_user['username']}")
            print(f"deposit : {self.authentication.current_user['balance']}")
            print("\n1. increse balance ")
            print("2. view availble trips")
            print("3. purchase ticket")
            print("4. change password")
            print("5. exit")
            
            choice = input("\nplease insert your option: ")
            
            if choice == '1':
                self.increase_balance()
            elif choice == '2':
                self.show_ticket_history()
            elif choice == '3':
                self.purchase_ticket()
            elif choice == '4':
                self.change_password()
            elif choice == '5':
                self.authentication.current_user = None
                break
            else:
                input("invalid option press enter to exit")

    def increase_balance(self):
        if not self.authentication.current_user:
            print("No user logged in")
            return
            
        self.clear_screen()
        print("increase balance")
        try:
            amount = float(input("input an amount: "))
            if amount <= 0:
                print("amount must be greater than zero")
            else:
                if self.trip_manager.increase_balance(self.authentication.current_user['id'], amount):
                    self.authentication.current_user['balance'] += amount
                    print(f"balance incresed successfully")
                else:
                    print("error in increse balance")
        except ValueError:
            print("invalid amount")
        input("press enter")

    def show_ticket_history(self):
        if not self.authentication.current_user:
            print("No user logged in")
            input("press enter")
            return
            
        self.clear_screen()
        print("trip history")
        
        tickets = self.trip_manager.get_user_tickets(self.authentication.current_user['id'])
        if not tickets:
            print("you have no trip")
        else:
            for ticket in tickets:
                print(f"ticket id : {ticket[0]}")
                print(f"cost : {ticket[1]}")
                print(f"started at : {ticket[2]}")
                print(f"end at : {ticket[3]}")
                print(f"purchase time : {ticket[4]}")
                print("-" * 40)
        
        input("press enter")

    def purchase_ticket(self):
        if not self.authentication.current_user:
            print("No user logged in")
            input("press enter")
            return
            
        self.clear_screen()
        print("purchase ticket")
        
        trips = self.trip_manager.get_available_trips()
        if not trips:
            print("there is no available trip")
            input("press enter")
            return
        
        for trip in trips:
            print(f"trip id {trip[0]} | cost : {trip[1]}  | started at : {trip[2]}")
        
        try:
            trip_id = int(input("\n please enter trip code: "))
            
            trip = self.trip_manager.get_trip(trip_id)
            if not trip:
                print("trip not found")
            else:
                try:
                    if self.trip_manager.purchase_ticket(self.authentication.current_user['id'], trip_id):
                        trip_cost = float(trip[1])
                        self.authentication.current_user['balance'] -= trip_cost
                        print("ticket buied successfully")
                    else:
                        print("error in buying ticket")
                except BalanceError as e:
                    print(f"{e.message}")
                except TripClose as e:
                    print(f"{e.message}")
                    
        except ValueError:
            print("invalid trip code")
        
        input("press enter")

    def change_password(self):
        if not self.authentication.current_user:
            print("No user logged in")
            input("press enter")
            return
            
        self.clear_screen()
        print("change password")
        new_password = input("new password: ")
        
        if self.authentication.change_password(new_password):
            print("password changed successfully")
        else:
            print("error in changing password")
        
        input("press enter")

    def admin_dashboard(self):
        while True:
            self.clear_screen()
            print("admin pannel")
            print("1. manage trips")
            print("2. view all users")
            print("3. exit")
            
            choice = input("\nplease insert your option: ")
            
            if choice == '1':
                self.manage_trips()
            elif choice == '2':
                self.show_all_users()
            elif choice == '3':
                self.is_superuser = False
                break
            else:
                input("invalid option press enter to exit")

    def manage_trips(self):
        while True:
            self.clear_screen()
            print("manage trips")
            print("1. add new trip")
            print("2. view all trip")
            print("3. verify trip")
            print("4. delete trip")
            print("5. trip start")
            print("6. return")
            
            choice = input("\nplease insert your option: ")
            
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
                input("invalid option press enter to exit")

    def add_trip(self):
        self.clear_screen()
        print("add new trip")
        try:
            cost = float(input("trip cost: "))
            start_time = input("start at (YYYY-MM-DD HH:MM:SS): ")
            end_time = input("end at  (YYYY-MM-DD HH:MM:SS): ")
            
            if not self._validate_date(start_time) or not self._validate_date(end_time):
                print("Invalid date format! Use: 2024-01-01 10:00:00")
                input("press enter")
                return
            
            if self.trip_manager.create_trip(cost, start_time, end_time):
                print("trip add suuccessfully")
            else:
                print("error in adding trip")
        except ValueError:
            print("value error")
        input("press enter")

    def _validate_date(self, date_string):
        try:
            datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            return True
        except ValueError:
            return False

    def show_all_trips(self):
        self.clear_screen()
        print("all trips")
        
        query = "SELECT id, cost, start_time, end_time, is_started FROM trip ORDER BY start_time"
        trips = self.trip_manager.db.execute_select(query)
        
        if not trips:
            print("there is no trip")
        else:
            for trip in trips:
                status = "started" if trip[4] else "waiting"
                print(f"trip code : {trip[0]}")
                print(f"cost : {trip[1]}")
                print(f"start at : {trip[2]}")
                print(f"end at : {trip[3]}")
                print(f"status: {status}")
                print("-" * 40)
        
        input("press enter")

    def show_all_users(self):
        self.clear_screen()
        print("all users")
        
        users = self.trip_manager.get_all_users()
        if not users:
            print("there is no users")
        else:
            for user in users:
                print(f"user id : {user[0]}")
                print(f"username : {user[1]}")
                print(f"balance : {user[2]}")
                print(f"register at : {user[3]}")
                print("-" * 40)
        
        input("press enter")

    def edit_trip(self):
        self.clear_screen()
        print("verify trip")
        
        trip_id = input("please insert trip code: ")
        if not trip_id.isdigit():
            print("invalid trip code")
            input("press enter")
            return
        
        trip = self.trip_manager.get_trip(int(trip_id))
        if not trip:
            print("trip not found")
            input("press enter")
            return
        
        try:
            cost = float(input(f"new_cost [{trip[1]}]: ") or trip[1])
            start_time = input(f"new start time [{trip[2]}]: ") or trip[2]
            end_time = input(f"new end time [{trip[3]}]: ") or trip[3]
            
            if self.trip_manager.update_trip(int(trip_id), cost, start_time, end_time):
                print("trip update successfully")
            else:
                print("error in update trip")
        except ValueError:
            print("invalid value")
        input("press enter")

    def delete_trip(self):
        self.clear_screen()
        print("delete trip")
        
        trip_id = input("please input trip code : ")
        if not trip_id.isdigit():
            print("invalid trip code")
            input("press enter")
            return
        
        confirm = input("are u sure u want delete this trip? (y/n): ")
        if confirm.lower() == 'y':
            if self.trip_manager.delete_trip(int(trip_id)):
                print("trip delete successfully")
            else:
                print("error in deleting trip")
        
        input("press enter")

    def start_trip(self):
        self.clear_screen()
        print("start trip")
        
        trip_id = input("please input trip code :")
        if not trip_id.isdigit():
            print("invalid trip code")
            input("press enter")
            return
        
        if self.trip_manager.start_trip(int(trip_id)):
            print("trip started successfully")
        else:
            print("error in starting trip")
        
        input("press enter")

if __name__ == "__main__":
    cli = CLI()
    cli.show_main_menu()