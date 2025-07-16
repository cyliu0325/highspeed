import requests
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

FROM_STATION = "05"  # 台中
TO_STATION = "01"    # 台北
DATE = "2024/07/20"
START_HOUR = 14
END_HOUR = 17
INTERVAL = 600  # 每10分鐘查詢一次

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

def check_ticket():
    url = "https://www.thsrc.com.tw/TimeTable/Search"
    headers = {"Content-Type": "application/json"}
    found_times = []

    for hour in range(START_HOUR, END_HOUR):
        time_str = f"{hour:02d}:00"
        data = {
            "TrainDate": DATE,
            "OriginStation": FROM_STATION,
            "DestinationStation": TO_STATION,
            "TimeSelect": "DepartureInMandarin",
            "OutWardSearchTime": time_str
        }

        r = requests.post(url, headers=headers, json=data)
        if r.status_code != 200:
            print(f"[{datetime.now()}] 查詢失敗")
            continue

        if '尚有座位' in r.text or '對號座' in r.text:
            found_times.append(time_str)

    return found_times

def send_email(times):
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = TO_EMAIL
    msg["Subject"] = "🚄 高鐵有票啦！"

    body = "以下時段有票：\n" + "\n".join(times)
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, TO_EMAIL, msg.as_string())

    print(f"[{datetime.now()}] 已寄出通知 Email")

def main():
    while True:
        print(f"[{datetime.now()}] 正在查票...")
        result = check_ticket()
        if result:
            send_email(result)
            break
        else:
            print("目前查無票，下次再查")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
