from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, requests

app = Flask(__name__)
CORS(app)
ACCOUNT_SERVICE = 'http://localhost:5002'

def db():
    conn = sqlite3.connect('transactions.db')
    conn.row_factory = sqlite3.Row
    return conn

def record(acc_no, ttype, amount):
    with db() as conn:
        conn.execute("INSERT INTO transactions(account_number,type,amount) VALUES(?,?,?)",
                     (acc_no, ttype, amount))

@app.route('/deposit', methods=['POST'])
def deposit():
    d = request.json
    if d['amount'] <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400
    r = requests.post(f'{ACCOUNT_SERVICE}/deposit', json=d)
    if r.status_code == 200:
        record(d['account_number'], 'DEPOSIT', d['amount'])
        return jsonify({'message': f"Deposited {d['amount']}"})
    return jsonify(r.json()), r.status_code

@app.route('/withdraw', methods=['POST'])
def withdraw():
    d = request.json
    if d['amount'] <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400
    r = requests.post(f'{ACCOUNT_SERVICE}/withdraw', json=d)
    if r.status_code == 200:
        record(d['account_number'], 'WITHDRAW', d['amount'])
        return jsonify({'message': f"Withdrew {d['amount']}"})
    return jsonify(r.json()), r.status_code

@app.route('/transfer', methods=['POST'])
def transfer():
    d = request.json
    src, dst, amt = d['from_account'], d['to_account'], d['amount']
    if amt <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400
    r1 = requests.post(f'{ACCOUNT_SERVICE}/withdraw', json={'account_number': src, 'amount': amt})
    if r1.status_code != 200:
        return jsonify(r1.json()), r1.status_code
    r2 = requests.post(f'{ACCOUNT_SERVICE}/deposit', json={'account_number': dst, 'amount': amt})
    if r2.status_code != 200:   # compensate: undo withdrawal (Saga-style rollback)
        requests.post(f'{ACCOUNT_SERVICE}/deposit', json={'account_number': src, 'amount': amt})
        return jsonify({'error': 'Transfer failed, rolled back'}), 400
    record(src, 'TRANSFER_OUT', amt)
    record(dst, 'TRANSFER_IN', amt)
    return jsonify({'message': f'Transferred {amt} from {src} to {dst}'})

@app.route('/transactions/<int:acc_no>', methods=['GET'])
def history(acc_no):
    rows = db().execute("SELECT * FROM transactions WHERE account_number=? ORDER BY id DESC",
                        (acc_no,)).fetchall()
    return jsonify([dict(r) for r in rows])

if __name__ == '__main__':
    with sqlite3.connect('transactions.db') as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number INTEGER, type TEXT, amount REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    app.run(port=5003)