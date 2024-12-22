from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ScheduledSMS(db.Model):
    __tablename__ = "scheduled_sms"

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(50), nullable=False)
    message_body = db.Column(db.String(255), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=True)