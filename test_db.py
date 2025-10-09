import psycopg2

try:
    con = psycopg2.connect(
        host="127.0.0.1",
        port="5432", 
        database="terminal",
        user="postgres",
        password="123"  
    )
    print("create connection succesfully")
    con.close()
except Exception as e:
    print(f"error : {e}")