from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
import pytz
from send_sms import send_sms  # 上記で修正した Vonage新版コード
import os

JST = pytz.timezone("Asia/Tokyo")

app = Flask(__name__)

scheduled_messages = []
next_id = 1

def parse_jst_datetime(input_str):
    naive_dt = datetime.strptime(input_str, "%Y-%m-%dT%H:%M")
    return JST.localize(naive_dt)

def get_jst_now():
    return datetime.now(JST)

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

            jst_dt = parse_jst_datetime(scheduled_str)

            new_msg = {
                "id": next_id,
                "phone_number": phone_number,
                "message_body": message_body,
                "scheduled_time": jst_dt,
                "sent_at": None
            }
            scheduled_messages.append(new_msg)
            next_id += 1

        return redirect(url_for("index"))

    return render_template("index.html", scheduled_sms_list=scheduled_messages)

@app.route("/manual_send", methods=["POST"])
def manual_send():
    """
    「手動送信」ボタンを押すと、
    送信予定時刻 <= 現在(JST) かつ 未送信 のメッセージをまとめて送る
    """
    now_jst = get_jst_now()
    for msg in scheduled_messages:
        if msg["sent_at"] is None and msg["scheduled_time"] <= now_jst:
            try:
                send_sms(msg["phone_number"], msg["message_body"])
                msg["sent_at"] = now_jst
            except Exception as e:
                print(f"Error sending SMS to {msg['phone_number']}: {e}")
    return redirect(url_for("index"))

@app.route("/delete", methods=["POST"])
def delete_message():
    message_id = int(request.form.get("message_id"))
    global scheduled_messages
    scheduled_messages = [m for m in scheduled_messages if m["id"] != message_id]
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
