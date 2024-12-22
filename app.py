from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
import pytz
import os

from send_sms import send_sms  # VonageやTwilio等、好みのSMS送信用関数をインポート

JST = pytz.timezone("Asia/Tokyo")

app = Flask(__name__)

# メモリ上で管理するため、再起動で消える
scheduled_messages = []
next_id = 1

def parse_jst_datetime(input_str):
    """
    "2025-01-01T09:00" (datetime-local) を 日本時間(JST)の datetime に変換
    """
    naive_dt = datetime.strptime(input_str, "%Y-%m-%dT%H:%M")
    return JST.localize(naive_dt)

def get_jst_now():
    return datetime.now(JST)

@app.route("/", methods=["GET", "POST"])
def index():
    global next_id

    if request.method == "POST":
        # メッセージ登録
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

    # GET: 一覧を表示
    return render_template("index.html", scheduled_sms_list=scheduled_messages)

@app.route("/manual_send", methods=["POST"])
def manual_send():
    """
    「手動送信」ボタンが押されたら、
    送信予定時刻 <= 現在JST かつ 未送信 のメッセージを一括送信
    """
    now_jst = get_jst_now()
    for msg in scheduled_messages:
        if msg["sent_at"] is None and msg["scheduled_time"] <= now_jst:
            try:
                send_sms(msg["phone_number"], msg["message_body"])
                msg["sent_at"] = now_jst  # 送信完了をJST時刻で記録
            except Exception as e:
                print(f"Error sending SMS to {msg['phone_number']}: {e}")

    return redirect(url_for("index"))

@app.route("/delete", methods=["POST"])
def delete_message():
    """
    一覧からメッセージを削除
    """
    message_id = int(request.form.get("message_id"))
    global scheduled_messages
    scheduled_messages = [m for m in scheduled_messages if m["id"] != message_id]
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
