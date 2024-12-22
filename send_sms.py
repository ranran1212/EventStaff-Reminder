import os
from vonage import Vonage, Auth
from vonage_sms import SmsMessage, SmsResponse

VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")
VONAGE_VIRTUAL_NUMBER = os.environ.get("VONAGE_VIRTUAL_NUMBER")

def send_sms(to_number: str, message_body: str):
    """
    Vonageの新版SDKでSMSを送る例:
      1. Authオブジェクト
      2. Vonageインスタンス
      3. SmsMessageオブジェクト
      4. vonage_client.sms.send(...)を呼ぶ
    """
    # 認証情報の作成
    auth = Auth(api_key=VONAGE_API_KEY, api_secret=VONAGE_API_SECRET)

    # Vonageインスタンス作成
    vonage_client = Vonage(auth=auth)  # ここが旧Clientと違う

    # SMS送信メッセージモデルを作成
    print(message_body)
    message = SmsMessage(to=to_number, from_=VONAGE_VIRTUAL_NUMBER, text=message_body, data_coding='unicode')

    # 送信
    response: SmsResponse = vonage_client.sms.send(message)

    # Pydanticモデルを使ったレスポンスなので、model_dump()等で内容を確認可能
    if response.messages[0].status == "0":
        print("Message sent successfully via Vonage new API.")
    else:
        error_text = response.messages[0].error_text
        raise RuntimeError(f"Vonage SMS failed: {error_text}")
