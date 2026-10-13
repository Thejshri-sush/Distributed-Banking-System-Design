Distributed Banking System Design

A micro-project demonstrating Software Engineering and Agile/Scrum practicesby building a distributed banking system with 3 independent REST microservices.

Architecture

Customer Service (port 5001) — register, login → customers.db
Account Service (port 5002) — accounts, deposit, withdraw → accounts.db
Transaction Service (port 5003) — transfer, history → transactions.db
Frontend — HTML/JS page calling all three servicesEach service owns its own SQLite database and communicates over REST.
How to Run

pip3 install flask flask-cors requests
python3 app.py (inside each of the 3 service folders)
Open frontend/index.html in a browser
Features

Register/Login, Create Account, Balance, Deposit, Withdraw (insufficient-fundscheck), Transfer (with compensating rollback when destination fails),Transaction History.

Tech Stack

Python, Flask, SQLite, HTML/JavaScript, Postman (testing), draw.io (diagrams)

Team

Scrum team of 5 — Product Owner, Scrum Master, 2 Developers.Developed in 3 sprints with daily standups, sprint review, and retrospective.

