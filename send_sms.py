# send_sms.py
import os
import vonage

VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")
VONAGE_VIRTUAL_NUMBER = os.environ.get("VONAGE_VIRTUAL_NUMBER")
"""
例:
VONAGE_API_KEY=xxxx
VONAGE_API_SECRET=yyyy
VONAGE_VIRTUAL_NUMBER=+1234567890
"""

def send_sms(to_number: str, message_body: str):
    """
    Vonage APIを使ってSMSを送信
    :param to_number: 送信先電話番号 (国際形式)
    :param message_body: 送信する本文
    """
    client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
    sms = vonage.Sms(client)

    responseData = sms.send_message(
        {
            "from": VONAGE_VIRTUAL_NUMBER,
            "to": to_number,
            "text": message_body,
        }
    )

    # レスポンスを確認
    if responseData["messages"][0]["status"] == "0":
        print(f"Sent message to {to_number} successfully.")
    else:
        print(f"Failed to send message: {responseData['messages'][0]['error-text']}")
