# scheduler.py (例)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from send_sms import send_sms

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///test.db")
db = SQLAlchemy(app)

class ScheduledSMS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(50), nullable=False)
    message_body = db.Column(db.String(255), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=True)

def check_and_send_sms():
    now = datetime()
    unsent_messages = ScheduledSMS.query.filter(
        ScheduledSMS.sent_at.is_(None),
        ScheduledSMS.scheduled_time <= now
    ).all()

    for sms_job in unsent_messages:
        try:
            send_sms(sms_job.phone_number, sms_job.message_body)
            sms_job.sent_at = datetime()
            db.session.commit()
        except Exception as e:
            print(f"Error sending SMS to {sms_job.phone_number}: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(check_and_send_sms, 'interval', minutes=1)
scheduler.start()

@app.route("/")
def index():
    return "Scheduler is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)