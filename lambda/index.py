import json
import os
import re
import urllib.request
import urllib.error

# Lambda コンテキストからリージョンを抽出する関数
def extract_region_from_arn(arn):
    match = re.search('arn:aws:lambda:([^:]+):', arn)
    if match:
        return match.group(1)
    return "us-east-1"

# FastAPIのエンドポイントURLを環境変数から取得（デフォルト: /generate）
FASTAPI_SERVER_URL = os.environ.get("FASTAPI_SERVER_URL", "http://localhost:8000/generate")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # ユーザー情報のログ出力（必要に応じて）
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        # リクエストボディをパース
        body = json.loads(event['body'])
        message = body['message']

        print("Processing message:", message)

        # FastAPIに送るリクエストペイロード（generateエンドポイントに合わせて修正）
        payload = {
            "prompt": message,
            "max_new_tokens": 128,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }

        print("Calling FastAPI server with payload:", json.dumps(payload))

        # POSTリクエスト送信
        req = urllib.request.Request(
            FASTAPI_SERVER_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                response_body = response.read()
                response_data = json.loads(response_body.decode('utf-8'))
                print("FastAPI server response:", json.dumps(response_data))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise Exception(f"FastAPI server HTTP error: {e.code}, {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"FastAPI server URL error: {e.reason}")

        # レスポンスの成功確認と抽出
        assistant_response = response_data.get('generated_text', '[no response]')
        response_time = response_data.get('response_time', 0)

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
                "responseTime": response_time
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
