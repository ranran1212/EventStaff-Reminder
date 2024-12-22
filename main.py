from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from send_sms import send_sms

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///test.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class ScheduledSMS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(50), nullable=False)
    message_body = db.Column(db.String(255), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=True)

# DB初期化(本番ではFlask-Migrateが望ましい)
db.create_all()

# APScheduler 設定
scheduler = BackgroundScheduler()

def check_and_send_sms():
    with app.app_context():  # コンテキスト必須
        now = datetime.utcnow()
        unsent_messages = ScheduledSMS.query.filter(
            ScheduledSMS.sent_at.is_(None),
            ScheduledSMS.scheduled_time <= now
        ).all()

        for sms_job in unsent_messages:
            try:
                send_sms(sms_job.phone_number, sms_job.message_body)
                sms_job.sent_at = datetime.utcnow()
                db.session.commit()
            except Exception as e:
                print(f"Error sending SMS to {sms_job.phone_number}: {e}")

scheduler.add_job(check_and_send_sms, 'interval', minutes=1)
scheduler.start()

# Flaskルート
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        phone_numbers = request.form.getlist("phone_number[]")
        message_bodies = request.form.getlist("message_body[]")
        scheduled_times = request.form.getlist("scheduled_time[]")

        for i in range(len(phone_numbers)):
            phone_number = phone_numbers[i]
            message_body = message_bodies[i]
            scheduled_time_str = scheduled_times[i]

            scheduled_time = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M")
            new_sms = ScheduledSMS(
                phone_number=phone_number,
                message_body=message_body,
                scheduled_time=scheduled_time
            )
            db.session.add(new_sms)

        db.session.commit()
        return redirect(url_for("index"))

    scheduled_sms_list = ScheduledSMS.query.order_by(ScheduledSMS.scheduled_time).all()
    return render_template("index.html", scheduled_sms_list=scheduled_sms_list)

if __name__ == "__main__":
    app.run(debug=True)
