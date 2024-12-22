# app.py
from flask import Flask, request, render_template, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
import pytz
from send_sms import send_sms

JST = pytz.timezone("Asia/Tokyo")

app = Flask(__name__)

# メモリ上でスケジュールデータを保持 (再起動で消える)
scheduled_messages = []
next_id = 1

# APScheduler
scheduler = BackgroundScheduler()

def get_jst_now():
    return datetime.now(JST)

def parse_jst_datetime(input_str):
    # "2024-12-31T09:00" → naive dt
    naive_dt = datetime.strptime(input_str, "%Y-%m-%dT%H:%M")
    return JST.localize(naive_dt)

def check_and_send_sms():
    print("DEBUG: APScheduler job started.")
    """
    1分おきに呼ばれるジョブ。
    送信予定時刻 <= 現在時刻 & 未送信のSMSを探してVonageで送信し、sent_atを更新する
    """
    now_jst = get_jst_now()
    print(f"check_and_send_sms called at {now_jst}")
    for msg in scheduled_messages:
        print(f"DEBUG: checking msg.id={msg['id']} at {now_jst}, scheduled={msg['scheduled_time']}")
        if msg["scheduled_time"] <= now_jst and msg["sent_at"] is None:
            try:
                send_sms(msg["phone_number"], msg["message_body"])
                msg["sent_at"] = datetime.utcnow()
            except Exception as e:
                print(f"Error sending SMS to {msg['phone_number']}: {e}")

# ジョブを1分間隔で実行
scheduler.add_job(check_and_send_sms, 'interval', minutes=1)
scheduler.start()

@app.route("/", methods=["GET", "POST"])
def index():
    global next_id

    if request.method == "POST":
        phone_numbers = request.form.getlist("phone_number[]")
        message_bodies = request.form.getlist("message_body[]")
        scheduled_times = request.form.getlist("scheduled_time[]")

        for i in range(len(phone_numbers)):
            phone_number = phone_numbers[i]
            message_body = message_bodies[i]
            scheduled_str = scheduled_times[i]

            # HTML5 datetime-localの場合、"YYYY-MM-DDTHH:MM" 形式になる
            # "2025-01-01T09:00" のような文字列を datetime にパース
            scheduled_dt = datetime.strptime(scheduled_str, "%Y-%m-%dT%H:%M")

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

    # GET: 一覧表示
    return render_template("index.html", scheduled_sms_list=scheduled_messages)

@app.route("/delete", methods=["POST"])
def delete_message():
    """
    一覧から削除するボタンを押されたときに呼ばれる
    """
    message_id = int(request.form.get("message_id"))
    global scheduled_messages
    scheduled_messages = [ msg for msg in scheduled_messages if msg["id"] != message_id ]
    return redirect(url_for("index"))

if __name__ == "__main__":
    # ローカル実行用
    app.run(debug=True)
