import os
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime

# 環境変数の読み込み
load_dotenv()

# Twitter APIの設定
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
USER_IDS = ["1214338734126026752"]  # ユーザーIDを11件指定

# Google Sheets APIの設定
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # ダウンロードしたサービスアカウントJSONファイル
SPREADSHEET_ID = "1tw1zJxAthxaof2T90IR6LK0xN0BFc-yiVl_cc7vsLlQ"  # GoogleスプレッドシートID
RANGE_NAME = 'Sheet1!A2'

# Google Sheets APIの認証情報を作成
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# Twitter APIリクエストを送信してデータを取得
def get_user_data(user_id):
    url = f"https://api.twitter.com/2/users/{user_id}?user.fields=public_metrics"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("Twitter API response:", data)  # デバッグ用に追加
        followers_count = data['data']['public_metrics']['followers_count']
        following_count = data['data']['public_metrics']['following_count']
        return followers_count, following_count
    else:
        print(f"Error fetching data for user {user_id}: {response.status_code}")
        return None, None

# Google Sheetsに書き込む
def update_google_sheet(data):
    print("Data to be written to Google Sheets:", data)  # デバッグ用に追加
    sheet = service.spreadsheets()
    body = {'values': data}
    result = sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
                                   valueInputOption="RAW", body=body).execute()
    print(f"Updated {result.get('updates').get('updatedCells')} cells.")

# 11アカウントに対してデータを取得してスプレッドシートに記録
def collect_and_record_data():
    data = []
    for user_id in USER_IDS:
        followers, following = get_user_data(user_id)
        if followers is not None and following is not None:
            row = [user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), followers, following]
            data.append(row)
    
    if data:
        update_google_sheet(data)

if __name__ == "__main__":
    collect_and_record_data()
