# app.py
from flask import Flask, request, render_template, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
import pytz

# Vonage等のSMS送信用モジュール
from send_sms import send_sms

# --- ここで JST を定義 ---
JST = pytz.timezone("Asia/Tokyo")

app = Flask(__name__)

# メモリ上でスケジュールデータを保持 (再起動で消える)
scheduled_messages = []
next_id = 1

# APScheduler
scheduler = BackgroundScheduler()

def get_jst_now():
    """現在のJST時刻を返す"""
    return datetime.now(JST)

def parse_jst_datetime(input_str):
    """
    HTML5のdatetime-localで入力された文字列(例: "2025-01-01T09:00")を
    JSTの datetimeオブジェクトに変換する
    """
    naive_dt = datetime.strptime(input_str, "%Y-%m-%dT%H:%M")
    jst_dt = JST.localize(naive_dt)  # "naive"なdtをJSTタイムゾーン付きdtに
    return jst_dt

def check_and_send_sms():
    """
    1分おきに呼ばれるジョブ。
    [送信予定時刻 <= 現在JST] & 未送信 のメッセージをVonageで送信し、sent_atをJSTで更新
    """
    now_jst = get_jst_now()
    print("DEBUG: APScheduler job started.")
    print(f"check_and_send_sms called at {now_jst}")

    for msg in scheduled_messages:
        print(f"DEBUG: checking msg.id={msg['id']} at {now_jst}, scheduled={msg['scheduled_time']}")
        # scheduled_timeとsent_atの比較もJSTで行う
        if msg["sent_at"] is None and msg["scheduled_time"] <= now_jst:
            try:
                send_sms(msg["phone_number"], msg["message_body"])
                # 送信完了したら JST の現在時刻を記録
                msg["sent_at"] = get_jst_now()
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

            # "2025-01-01T09:00" (HTML5 datetime-local) → JSTのdatetime
            scheduled_dt = parse_jst_datetime(scheduled_str)

            new_msg = {
                "id": next_id,
                "phone_number": phone_number,
                "message_body": message_body,
                "scheduled_time": scheduled_dt,  # JSTで保持
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
    scheduled_messages = [m for m in scheduled_messages if m["id"] != message_id]
    return redirect(url_for("index"))

if __name__ == "__main__":
    # ローカル実行用
    app.run(debug=True)
