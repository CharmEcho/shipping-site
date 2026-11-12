from datetime import datetime
import uuid
from flask_login import UserMixin
from .extensions import db, bcrypt


# ------------------------------
# USER MODEL
# ------------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    shipments = db.relationship("Shipment", backref="user", lazy=True)
    payments = db.relationship("Payment", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


# ------------------------------
# SHIPMENT MODEL
# ------------------------------
class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Float, nullable=False, default=0.0)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)
    sender_name = db.Column(db.String(120), nullable=False)
    receiver_name = db.Column(db.String(120), nullable=False)
    origin = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()

    @staticmethod
    def generate_tracking_number():
        return f"TRK-{uuid.uuid4().hex[:10].upper()}"

    def __repr__(self):
        return f"<Shipment {self.tracking_number}>"

# ------------------------------
# TRACKING MODEL
# ------------------------------
class Tracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100), nullable=False)  # e.g., "Arrived at sorting center"
    location = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    shipment_id = db.Column(db.Integer, db.ForeignKey("shipment.id"), nullable=False)

    def __repr__(self):
        return f"<Tracking {self.status} at {self.location}>"

# ------------------------------
# PAYMENT MODEL
# ------------------------------
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(50), nullable=False)  # e.g., Card, PayPal
    status = db.Column(db.String(50), default="Pending")  # Pending, Completed, Failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    shipment_id = db.Column(db.Integer, db.ForeignKey("shipment.id"), nullable=False)

    def __repr__(self):
        return f"<Payment {self.amount} for Shipment {self.shipment_id}>"
