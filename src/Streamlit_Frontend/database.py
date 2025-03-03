import sqlite3
import bcrypt

# Function to get a new database connection
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # Allows you to access columns by name
    return conn

# Create the users table if it doesn't already exist
def create_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Add a new user to the database
def add_user(username, name, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute('INSERT INTO users (username, name, password) VALUES (?, ?, ?)', 
                       (username, name, hashed_password))
        conn.commit()
        return "User added successfully!"
    except sqlite3.IntegrityError:
        return "Username already exists."
    finally:
        conn.close()

# Authenticate user by comparing the provided password with the stored hashed password
def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_password = result[0]
        # Verify password
        if bcrypt.checkpw(password.encode(), stored_password):
            return True
    return False
