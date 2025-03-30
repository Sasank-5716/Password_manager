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
    
    pass

if __name__ == "__main__":
    main()