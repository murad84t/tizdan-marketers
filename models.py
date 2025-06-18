from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(50),  nullable=False)
    username = db.Column(db.String(30),  unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role     = db.Column(db.String(10),  default='marketer')  # or 'admin'
    txns     = db.relationship('Transaction', backref='user', lazy=True)

    # convenience helpers
    def balance(self, start, end):
        return sum(t.amount for t in self.txns
                   if start <= t.timestamp.date() <= end)

    def transactions_between(self, start, end):
        return [t for t in self.txns
                if start <= t.timestamp.date() <= end]


class Transaction(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    amount    = db.Column(db.Float, nullable=False)  # +ve deposit / -ve withdraw
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
