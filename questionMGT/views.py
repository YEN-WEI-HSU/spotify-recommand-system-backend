from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

DIFY_API_URL = "http://35.221.178.11/v1/chat-messages"  # 改成正確 port
DIFY_API_KEY = "app-pNJOu5gCreEDY5FpTTc0Hiok"

@csrf_exempt
def ask_question(request):
    print("🚀 API 進入 /api/question/ask/")  # 確認 view 被呼叫了

    if request.method == "POST":
        try:
            print("📩 開始解析 body...")
            data = json.loads(request.body)
            print("📨 接收到資料：", data)

            user_question = data.get("question", "")
            if not user_question:
                return JsonResponse({"error": "未提供問題內容"}, status=400)

            print("📡 發送到 Dify...")
            response = requests.post(
                DIFY_API_URL,
                headers={
                    "Authorization": f"Bearer {DIFY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": {},
                    "query": user_question,
                    "user": "demo-user",   # ← 這行是關鍵！用任何唯一字串代表使用者
                    "response_mode": "blocking"
                },
                timeout=30
            )

            print("📬 Dify 狀態碼：", response.status_code)
            print("📦 Dify 回傳：", response.text)

            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "Dify 沒有提供回答")
                return JsonResponse({"answer": answer})
            else:
                return JsonResponse({
                    "error": "Dify 回傳錯誤",
                    "status_code": response.status_code,
                    "message": response.text
                }, status=500)

        except Exception as e:
            print("❌ API 發生錯誤：", str(e))
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST allowed"}, status=405)
