from django.shortcuts import render

# Create your views here.


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def ask_question(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question", "")
            return JsonResponse({"answer": f"你問了：{question}"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST allowed"}, status=405)
