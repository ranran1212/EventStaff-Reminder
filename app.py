from flask import Flask, request, render_template, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from send_sms import send_sms

app = Flask(__name__)

# メモリ上で管理するスケジュールリスト
# 例: [{"id": 1, "phone_number": "+81...", "message_body": "...", "scheduled_time": datetime(2025,1,1,9,0), "sent_at": None}, ...]
scheduled_messages = []
next_id = 1  # メモリ上で採番する簡易的なID

# APScheduler
scheduler = BackgroundScheduler()

def check_and_send_sms():
    """
    1分おきに呼ばれるジョブ。
    'scheduled_messages' から送信すべきSMSを探してTwilio送信する。
    """
    now = datetime.now()
    for msg in scheduled_messages:
        # 送信済みでない & 予定時刻 <= 現在時刻
        if msg["sent_at"] is None and msg["scheduled_time"] <= now:
            try:
                send_sms(msg["phone_number"], msg["message_body"])
                msg["sent_at"] = datetime.now()
                print(f"Sent SMS to {msg['phone_number']}")
            except Exception as e:
                print(f"Error sending SMS to {msg['phone_number']}: {e}")

# APSchedulerのジョブ登録: 1分ごとに check_and_send_sms
scheduler.add_job(check_and_send_sms, 'interval', minutes=1)
scheduler.start()

@app.route("/", methods=["GET", "POST"])
def index():
    global next_id

    if request.method == "POST":
        # フォームから受け取った複数行分のデータ
        phone_numbers = request.form.getlist("phone_number[]")
        message_bodies = request.form.getlist("message_body[]")
        scheduled_times = request.form.getlist("scheduled_time[]")

        for i in range(len(phone_numbers)):
            phone_number = phone_numbers[i]
            message_body = message_bodies[i]
            scheduled_time_str = scheduled_times[i]

            # 文字列 "2025-01-01 09:00" などを datetime に変換
            # タイムゾーンはUTC前提にしています。日本時間は別途対応が必要
            scheduled_dt = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M")

            new_msg = {
                "id": next_id,
                "phone_number": phone_number,
                "message_body": message_body,
                "scheduled_time": scheduled_dt,
                "sent_at": None
            }
            scheduled_messages.append(new_msg)
            next_id += 1

        return redirect(url_for("index"))

    # 一覧表示用: メモリ上の scheduled_messages を送る
    return render_template("index.html", scheduled_sms_list=scheduled_messages)

if __name__ == "__main__":
    app.run(debug=True)
