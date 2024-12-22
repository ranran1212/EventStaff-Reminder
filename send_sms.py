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
    client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
    sms = vonage.Sms(client)

    response_data = sms.send_message(
        {
            "from": VONAGE_FROM_NUMBER,
            "to": to_number,
            "text": message_body,
        }
    )

    if response_data["messages"][0]["status"] == "0":
        print("Message sent successfully.")
    else:
        print(f"Message failed with error: {response_data['messages'][0]['error-text']}")
