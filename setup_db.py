import mysql.connector

# Connect to the local MySQL server
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="AN56@pari",
    database="companydb"
)

cursor = db.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
)
""")

# Insert default admin user if not exists
cursor.execute("SELECT * FROM users WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")

# Create leaves table
cursor.execute("""
CREATE TABLE IF NOT EXISTS leaves (
    leave_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending'
)
""")

db.commit()
print("Database schema successfully set up! Added default user -> admin / admin123")
db.close()
