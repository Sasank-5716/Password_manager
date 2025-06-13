# main.py
import sqlite3
import hashlib
import secrets
import string
from cryptography.fernet import Fernet
import getpass
import argparse

class PasswordManager:
    
    def _get_fernet(self):
        # Load or generate encryption key
        try:
            with open(self.key_file, "rb") as f:
                key = f.read()
        except FileNotFoundError:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
        except IOError as e:  
            raise RuntimeError(f"Key file error: {str(e)}") 
    
        return Fernet(key)
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
    
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                master_password_hash TEXT NOT NULL
            )
        ''')
    
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                service TEXT NOT NULL,
                username TEXT,
                encrypted_password TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
    
        conn.commit()
        conn.close()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
        
    def register(self, username, master_password):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
    
        try:
            password_hash = self._hash_password(master_password)
            cursor.execute('''
                INSERT INTO users (username, master_password_hash)
                VALUES (?, ?)
            ''', (username, password_hash))
            conn.commit()
            print("Registration successful!")
        except sqlite3.IntegrityError:
            print("Username already exists!")
        finally:
            conn.close()

    def login(self, username, master_password):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
    
        cursor.execute('''
            SELECT id, master_password_hash FROM users WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()
        conn.close()
    
        if result and result[1] == self._hash_password(master_password):
            return result[0]  # Return user_id
        return None


    
    def add_password(self, user_id, service, username, password):
        encrypted_password = self.fernet.encrypt(password.encode()).decode()
    
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
    
        cursor.execute('''
            INSERT INTO passwords (user_id, service, username, encrypted_password)
            VALUES (?, ?, ?, ?)
        ''', (user_id, service, username, encrypted_password))
    
        conn.commit()
        conn.close()
        print("Password saved successfully!")

    def get_password(self, user_id, service):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
    
        cursor.execute('''
            SELECT username, encrypted_password FROM passwords 
            WHERE user_id = ? AND service = ?
        ''', (user_id, service))
        result = cursor.fetchone()
        conn.close()
    
        if result:
            username, encrypted_password = result
            password = self.fernet.decrypt(encrypted_password.encode()).decode()
            return username, password
        return None, None

    def list_services(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
    
        cursor.execute('''
            SELECT service FROM passwords WHERE user_id = ?
        ''', (user_id,))
        services = [row[0] for row in cursor.fetchall()]
        conn.close()
        return services
    
    def __init__(self, db_file="passwords.db"):
        self.db_file = db_file
        self.key_file = "secret.key"
        self.fernet = self._get_fernet()
        self._init_db()
    
    def generate_password(self, length=16):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(chars) for _ in range(length))

def main():
    parser = argparse.ArgumentParser(description="Password Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Register command
    register_parser = subparsers.add_parser("register", help="Register a new user")
    register_parser.add_argument("username", help="Username for the new account")
    
    # Login command
    login_parser = subparsers.add_parser("login", help="Login to your account")
    login_parser.add_argument("username", help="Your username")
    
    # Add password command
    add_parser = subparsers.add_parser("add", help="Add a new password")
    add_parser.add_argument("service", help="Service name (e.g., 'google')")
    add_parser.add_argument("--username", help="Username for the service")
    add_parser.add_argument("--password", help="Password for the service (leave empty to generate)")
    
    # Get password command
    get_parser = subparsers.add_parser("get", help="Get a stored password")
    get_parser.add_argument("service", help="Service name")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all stored services")
    
    args = parser.parse_args()
    pm = PasswordManager()
    
    if args.command == "register":
        password = getpass.getpass("Enter master password: ")
        confirm = getpass.getpass("Confirm master password: ")
        if password == confirm:
            pm.register(args.username, password)
        else:
            print("Passwords don't match!")
    
    elif args.command == "login":
        password = getpass.getpass("Enter master password: ")
        user_id = pm.login(args.username, password)
        if user_id:
            print("Login successful!")
            
            if hasattr(args, 'service'):  # For add/get commands after login
                if args.command == "add":
                    service_username = args.username if args.username else input("Enter service username: ")
                    service_password = args.password if args.password else pm.generate_password()
                    print(f"Generated password: {service_password}")
                    pm.add_password(user_id, args.service, service_username, service_password)
                
                elif args.command == "get":
                    username, password = pm.get_password(user_id, args.service)
                    if username and password:
                        print(f"Username: {username}")
                        print(f"Password: {password}")
                    else:
                        print("No password found for this service.")
            
            elif args.command == "list":
                services = pm.list_services(user_id)
                if services:
                    print("Your saved services:")
                    for service in services:
                        print(f"- {service}")
                else:
                    print("No saved services found.")
        else:
            print("Invalid username or password!")

if __name__ == "__main__":
    main()