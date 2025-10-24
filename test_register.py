from authentication import Authentication
from database import Database

def test_register():

    auth = Authentication()
    db = Database()
    
    test_username = "test"
    test_password = "123"
    
    print(f"register {test_username}")
    
    result = auth.register(test_username, test_password)
    
    if result:
        print("user registered")
    else:
        print("errorr in user register")
        return
  
    user_result = db.execute_select(
        "SELECT username, balance FROM users WHERE username = %s", 
        (test_username,)
    )
    
    if user_result:
        username, balance = user_result[0]
        print(f"user found in db")
  
    else:
        print("user not found in db")
        return
   
    db.execute_query("DELETE FROM users WHERE username = %s", (test_username,))
    print("test user deleted")
    
   
if __name__ == "__main__":
    test_register()