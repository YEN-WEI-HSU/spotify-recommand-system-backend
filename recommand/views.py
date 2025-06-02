from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from questionMGT.models import ChatRecord
import json
import requests
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

DIFY_API_KEY_TRACK = "app-86F0FXJmx6n8xTZ4c7S1yemq"
DIFY_API_KEY_ALBUM = "app-kietQPAYpWl9uAUfJdJRSu87"
DIFY_CHAT_ENDPOINT = "http://35.221.178.11/v1/chat-messages"
JWT_SECRET = os.getenv("JWT_SECRET", "default_fallback_secret")
JWT_ALGORITHM = "HS256"

@csrf_exempt
@require_http_methods(["POST"])
def album_recommendation(request):
    return handle_recommendation(
        request,
        prompt="請隨機推薦三張專輯",
        api_key=DIFY_API_KEY_ALBUM
    )

@csrf_exempt
@require_http_methods(["POST"])
def track_recommendation(request):
    return handle_recommendation(
        request,
        prompt="請隨機推薦五首歌",
        api_key=DIFY_API_KEY_TRACK
    )

def handle_recommendation(request, prompt, api_key):
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        user_id = None

        if token:
            try:
                decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                user_id = decoded.get("spotify_id")  # ✅ 跟你memberMGT一致
            except jwt.ExpiredSignatureError:
                print("⚠️ JWT 已過期")
            except jwt.InvalidTokenError as e:
                print(f"⚠️ JWT 無效：{e}")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": {},
            "query": prompt,
            "user": str(user_id) if user_id else "recommend-bot",
            "response_mode": "blocking"
        }

        response = requests.post(DIFY_CHAT_ENDPOINT, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "Dify 沒有提供回答")

            if user_id:
                ChatRecord.objects.create(
                    user_id=user_id,
                    question=prompt,
                    answer=answer
                )

            return JsonResponse({"answer": answer})
        else:
            return JsonResponse({
                "error": "Dify 回傳失敗",
                "status_code": response.status_code,
                "response": response.text
            }, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)