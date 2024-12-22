from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://eventstaff_reminder_database_user:RheFakdMI2wOOH6T6jMdwPxiWun3SBEI@dpg-ctk1ggdumphs73fdo7fg-a/eventstaff_reminder_database")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class ScheduledSMS(db.Model):
    """
    SMS 送信をスケジュールしたタスクを管理するテーブル
    """
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(50), nullable=False)
    message_body = db.Column(db.String(255), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=True)

# DBテーブル作成 (開発・テスト向け)
db.create_all()

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

            # 入力文字列 "2024-12-31 09:00" を datetime に変換 (フォーマットは要相談)
            scheduled_time = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M")

            new_sms = ScheduledSMS(
                phone_number=phone_number,
                message_body=message_body,
                scheduled_time=scheduled_time
            )
            db.session.add(new_sms)

        db.session.commit()
        return redirect(url_for("index"))

    # 予定が近い順に並べて表示
    scheduled_sms_list = ScheduledSMS.query.order_by(ScheduledSMS.scheduled_time).all()
    return render_template("index.html", scheduled_sms_list=scheduled_sms_list)

if __name__ == "__main__":
    # ローカル開発用: Flaskの開発サーバーで起動 (本番は gunicorn 等推奨)
    app.run(debug=True)
