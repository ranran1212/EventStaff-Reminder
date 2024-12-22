import os
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from send_sms import send_sms  # Twilio送信用
from models import db, ScheduledSMS  # モデルとdbオブジェクト

# Flaskアプリの作成
def create_app():
    app = Flask(__name__)
    # DB接続設定
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///test.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # DB初期化
    db.init_app(app)
    # Flask-Migrate初期化
    migrate = Migrate(app, db)

    # スケジューラ設定
    scheduler = BackgroundScheduler()

    # 定期実行関数
    def check_and_send_sms():
        with app.app_context():
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

    return app

# WSGI用のappを生成 (gunicornはここをエントリーポイントとして使う)
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)