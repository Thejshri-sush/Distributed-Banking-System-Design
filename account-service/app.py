from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def db():
    conn = sqlite3.connect('accounts.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_account(acc_no):
    return db().execute("SELECT * FROM accounts WHERE account_number=?", (acc_no,)).fetchone()

@app.route('/accounts', methods=['POST'])
def create_account():
    d = request.json
    with db() as conn:
        acc_no = conn.execute("SELECT COALESCE(MAX(account_number),1000)+1 FROM accounts").fetchone()[0]
        conn.execute("INSERT INTO accounts(account_number,customer_id,type,balance) VALUES(?,?,?,?)",
                     (acc_no, d['customer_id'], d.get('type', 'savings'), 0))
    return jsonify({'message': 'Account created', 'account_number': acc_no}), 201

@app.route('/accounts/<int:acc_no>', methods=['GET'])
def balance(acc_no):
    acc = get_account(acc_no)
    if not acc:
        return jsonify({'error': 'Account not found'}), 404
    return jsonify({'account_number': acc['account_number'], 'balance': acc['balance']})

@app.route('/deposit', methods=['POST'])
def deposit():
    d = request.json
    if not get_account(d['account_number']):
        return jsonify({'error': 'Account not found'}), 404
    with db() as conn:
        conn.execute("UPDATE accounts SET balance=balance+? WHERE account_number=?",
                     (d['amount'], d['account_number']))
    return jsonify({'message': 'Deposit successful'})

@app.route('/withdraw', methods=['POST'])
def withdraw():
    d = request.json
    acc = get_account(d['account_number'])
    if not acc:
        return jsonify({'error': 'Account not found'}), 404
    if acc['balance'] < d['amount']:
        return jsonify({'error': 'Insufficient balance'}), 400
    with db() as conn:
        conn.execute("UPDATE accounts SET balance=balance-? WHERE account_number=?",
                     (d['amount'], d['account_number']))
    return jsonify({'message': 'Withdrawal successful'})

if __name__ == '__main__':
    with sqlite3.connect('accounts.db') as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS accounts(
            account_number INTEGER PRIMARY KEY,
            customer_id INTEGER, type TEXT, balance REAL DEFAULT 0)""")
    app.run(port=5002)