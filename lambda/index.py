# lambda/index.py
import json
import os
import re
import requests  # HTTPリクエスト用に追加

# Lambda コンテキストからリージョンを抽出する関数（このままでOK）
def extract_region_from_arn(arn):
    match = re.search('arn:aws:lambda:([^:]+):', arn)
    if match:
        return match.group(1)
    return "us-east-1"

# FastAPIのエンドポイントURLを環境変数から取得（デフォルト localhost:8000）
FASTAPI_SERVER_URL = os.environ.get("https://7a84-34-169-221-171.ngrok-free.app/", "http://localhost:8000/chat")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # ユーザー情報（もし必要ならここで取得）
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        print("Processing message:", message)

        # FastAPIサーバーに送るペイロードを構築
        payload = {
            "message": message,
            "conversationHistory": conversation_history
        }

        print("Calling FastAPI server with payload:", json.dumps(payload))

        # FastAPIサーバーへリクエスト
        response = requests.post(FASTAPI_SERVER_URL, json=payload)

        if response.status_code != 200:
            raise Exception(f"FastAPI server error: {response.status_code}, {response.text}")

        response_data = response.json()
        print("FastAPI server response:", json.dumps(response_data))

        if not response_data.get('success'):
            raise Exception("FastAPI server returned failure")

        assistant_response = response_data['response']
        updated_conversation_history = response_data['conversationHistory']

        # 成功レスポンスの返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": updated_conversation_history
            })
        }

    except Exception as error:
        print("Error:", str(error))

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
