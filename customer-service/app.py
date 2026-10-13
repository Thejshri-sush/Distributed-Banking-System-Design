from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, hashlib

app = Flask(__name__)
CORS(app)

def db():
    conn = sqlite3.connect('customers.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['POST'])
def register():
    d = request.json
    if not d.get('name') or not d.get('email') or not d.get('password'):
        return jsonify({'error': 'All fields required'}), 400
    pw = hashlib.sha256(d['password'].encode()).hexdigest()
    try:
        with db() as conn:
            conn.execute("INSERT INTO customers(name,email,password) VALUES(?,?,?)",
                         (d['name'], d['email'], pw))
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 400
    return jsonify({'message': 'Registration successful'}), 201

@app.route('/login', methods=['POST'])
def login():
    d = request.json
    pw = hashlib.sha256(d['password'].encode()).hexdigest()
    row = db().execute("SELECT id,name FROM customers WHERE email=? AND password=?",
                       (d['email'], pw)).fetchone()
    if row:
        return jsonify({'message': 'Login successful', 'customer_id': row['id'], 'name': row['name']})
    return jsonify({'error': 'Invalid email or password'}), 401

if __name__ == '__main__':
    with sqlite3.connect('customers.db') as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS customers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)""")
    app.run(port=5001)