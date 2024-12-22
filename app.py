from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from models import db, ScheduledSMS

app = Flask(__name__)

# DB接続情報: 本番でRenderやHerokuを使うなら環境変数を参照
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql://eventstaff_reminder_database_user:RheFakdMI2wOOH6T6jMdwPxiWun3SBEI@dpg-ctk1ggdumphs73fdo7fg-a/eventstaff_reminder_database"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# models.py からインポートする
from models import db
db.init_app(app)

# もし models.py を使わずに直接app.pyで定義したい場合は:
#db = SQLAlchemy(app)

# Flask-Migrate 初期化
migrate = Migrate(app, db)

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
