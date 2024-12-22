from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
db = SQLAlchemy(app)

# Flask-Migrate 初期化
migrate = Migrate(app, db)

class ScheduledSMS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(50), nullable=False)
    message_body = db.Column(db.String(255), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=True)

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

            # 入力例 "2024-12-31 09:00" → datetime に変換
            scheduled_time = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M")

            new_sms = ScheduledSMS(
                phone_number=phone_number,
                message_body=message_body,
                scheduled_time=scheduled_time
            )
            db.session.add(new_sms)

        db.session.commit()
        return redirect(url_for("index"))

    # 送信予定日時が近い順に表示
    scheduled_sms_list = ScheduledSMS.query.order_by(ScheduledSMS.scheduled_time).all()
    return render_template("index.html", scheduled_sms_list=scheduled_sms_list)

if __name__ == "__main__":
    app.run()
