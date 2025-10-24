import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.conn = None  
        self.connect()
        if self.conn:  
            self.init_tables()  

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT')  
            )
            print("Database connection created successfully!")
        except Exception as e:
            print(f"Database connection error: {e}")
            
    def init_tables(self):
        if not self.conn:
            print("No database connection")
            return False
    
        try:
            with self.conn.cursor() as cur:
                cur.execute(""" 
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(100) NOT NULL,
                        balance DECIMAL(10,2) DEFAULT 0.00,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS trip (
                        id SERIAL PRIMARY KEY,
                        cost DECIMAL(10,2) NOT NULL,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP NOT NULL,
                        is_started BOOLEAN DEFAULT FALSE,
                        capacity INTEGER DEFAULT 40,
                        available_seats INTEGER DEFAULT 40,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ticket (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        trip_id INTEGER REFERENCES trip(id),
                        seat_number INTEGER,
                        status VARCHAR(20) DEFAULT 'RESERVED',
                        purchase_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        price DECIMAL(10,2) NOT NULL,
                        cancelled_at TIMESTAMP NULL
                );
            """)
            
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        amount DECIMAL(10,2) NOT NULL,
                        type VARCHAR(20) NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
                
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) NOT NULL,
                        action VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            self.conn.commit()
            print("Tables created successfully")
            return True

        except Exception as e:
            print(f"Table creation error: {e}")
            self.conn.rollback()
            return False
            
           
    def execute_query(self, query, params=None):
        if not self.conn:
            print("No database connection")
            return False
        
        try:
            
        
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
            
                if query.strip().upper().startswith('SELECT'):
                    result = cur.fetchall()
                    return result if result else []
                else:
                    self.conn.commit()  
                    return True
                
        except Exception as e:
            print(f"Query execution error: {e}")
            self.conn.rollback() 
            return False
        
    def execute_select(self, query, params=None):
        if not self.conn:
            print("No database connection")
            return []
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                result = cur.fetchall()
                return result if result else []
        except Exception as e:
            print(f"Select query error: {e}")
            self.conn.rollback()
            return []

    def close(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed")
            
        
            
        