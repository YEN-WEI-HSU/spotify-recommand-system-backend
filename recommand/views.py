from django.shortcuts import render

# Create your views here.


from django.http import JsonResponse

def recommend_view(request):
    return JsonResponse({"message": "This is the recommend API."})
