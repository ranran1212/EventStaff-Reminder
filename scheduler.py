from app import app, db, ScheduledSMS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from send_sms import send_sms

# APScheduler のバックグラウンドスケジューラ
scheduler = BackgroundScheduler()

def check_and_send_sms():
    """
    APSchedulerで1分おきに呼ばれる関数。
    Flaskコンテキスト外でDB操作するとエラーになるので、with app.app_context() を使う。
    """
    with app.app_context():
        now = datetime.utcnow()
        unsent_messages = ScheduledSMS.query.all()

        for sms_job in unsent_messages:
            try:
                # TwilioでSMS送信
                send_sms(sms_job.phone_number, sms_job.message_body)
                # 送信完了を記録
                sms_job.sent_at = datetime.utcnow()
                db.session.commit()
            except Exception as e:
                print(f"Error sending SMS to {sms_job.phone_number}: {e}")

# 1分ごとにcheck_and_send_smsを呼び出し
scheduler.add_job(check_and_send_sms, 'interval', minutes=1)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
