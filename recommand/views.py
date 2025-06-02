from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests

DIFY_API_URL = "http://35.221.178.11/v1/chat-messages"
DIFY_API_KEY = "app-你的金鑰"

@csrf_exempt
@require_http_methods(["POST"])
def album_recommendation(request):
    return handle_recommendation(request, "請推薦幾張適合放鬆的專輯")

@csrf_exempt
@require_http_methods(["POST"])
def track_recommendation(request):
    return handle_recommendation(request, "請推薦幾首輕鬆的歌")

def handle_recommendation(request, prompt):
    try:
        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": {},
            "query": prompt,
            "user": "recommend-bot",
            "response_mode": "blocking"
        }

        response = requests.post(DIFY_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            return JsonResponse({"answer": result.get("answer", "Dify 沒有提供回答")})
        else:
            return JsonResponse({"error": response.text}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)