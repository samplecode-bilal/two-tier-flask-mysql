import os
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb  # Import MySQLdb

app = Flask(__name__)

# Configure MySQL from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'default_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'default_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'default_db')

print("Debugging MySQL Connection:")
print(f"MYSQL_HOST: {app.config['MYSQL_HOST']}")
print(f"MYSQL_USER: {app.config['MYSQL_USER']}")
print(f"MYSQL_PASSWORD: {app.config['MYSQL_PASSWORD']}")
print(f"MYSQL_DB: {app.config['MYSQL_DB']}")

# Initialize MySQL
mysql = MySQL(app)

def init_db():
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message TEXT
            );
            ''')
            mysql.connection.commit()
            cur.close()
        print("Successfully created/verified the messages table.")
    
    except MySQLdb.OperationalError as e:
        print(f"Error connecting to or creating table: {e}")
        # Consider raising the exception or handling it more robustly
        # raise  # Re-raise the exception to prevent the app from running
        return  # Exit the function, preventing further execution

@app.route('/')
def hello():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT message FROM messages')
        messages = cur.fetchall()
        cur.close()
        return render_template('index.html', messages=messages)
    except MySQLdb.OperationalError as e:
        print(f"Error fetching messages: {e}")
        return "Error fetching messages from the database.", 500
    

@app.route('/submit', methods=['POST'])
def submit():
    try:
        new_message = request.form.get('new_message')
        if not new_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO messages (message) VALUES (%s)', (new_message,)) # Use tuple
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': new_message}), 200
    except MySQLdb.OperationalError as e:
        print(f"Error submitting message: {e}")
        return jsonify({'error': 'Failed to submit message'}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
