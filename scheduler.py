from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from send_sms import send_sms

from app import app, db, ScheduledSMS
from models import ScheduledSMS, db

scheduler = BackgroundScheduler()

def check_and_send_sms():
    with app.app_context():
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

# 1分ごとにジョブを実行
scheduler.add_job(check_and_send_sms, 'interval', minutes=1)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
