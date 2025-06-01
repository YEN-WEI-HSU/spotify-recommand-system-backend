from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ChatRecord
from memberMGT.services import check_jwt_tokens
import json
import requests

# 設定你的 Dify API 資訊
DIFY_API_URL = "http://35.221.178.11/v1/chat-messages"
DIFY_API_KEY = "app-pNJOu5gCreEDY5FpTTc0Hiok"


@csrf_exempt
@require_http_methods(["POST"])
def ask_question(request):
    print("🚀 API 進入 /back/question/ask/")
    jwt_token = request.headers.get("token")
    tokens = check_jwt_tokens(jwt_token) if jwt_token else None

    try:
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
                "user": tokens.spotify_id if tokens else "demo-user",  # 使用 Spotify ID 或 demo-user
                # "user": "demo-user",  # 可改成真正登入帳號
                "response_mode": "blocking"
            },
            timeout=300
        )

        print("📬 Dify 狀態碼：", response.status_code)
        print("📦 Dify 回傳：", response.text)

        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "Dify 沒有提供回答")

            user_id = tokens.spotify_id if tokens else "demo-user"
            # user_id = "demo-user"

            # ✅ 限制只保留 5 筆聊天紀錄
            existing_records = ChatRecord.objects.filter(user_id=user_id).order_by("-timestamp")
            if existing_records.count() >= 5:
                for record in existing_records[5:]:
                    record.delete()

            # ✅ 儲存新的紀錄
            ChatRecord.objects.create(
                user_id=user_id,
                question=user_question,
                answer=answer
            )

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


@require_http_methods(["GET"])
def chat_history(request):
    try:
        jwt_token = request.headers.get("token")
        tokens = check_jwt_tokens(jwt_token) if jwt_token else None
        user_id = tokens.spotify_id if tokens else "demo-user"  # 使用 Spotify ID 或 demo-user
        # user_id = "demo-user"  # 日後改為 request.user.username 等登入資料
        records = ChatRecord.objects.filter(user_id=user_id).order_by("-timestamp")[:5]

        data = [
            {
                "id": str(record.id),
                "question": record.question,
                "answer": record.answer,
                "timestamp": record.timestamp.isoformat(),
            }
            for record in records
        ]
        return JsonResponse({"history": data})
    except Exception as e:
        print("❌ 查詢歷史紀錄失敗：", str(e))
        return JsonResponse({"error": str(e)}, status=500)
