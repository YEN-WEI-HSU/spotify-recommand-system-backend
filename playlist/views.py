from django.shortcuts import render

# Create your views here.


from django.http import JsonResponse

def my_playlist_view(request):
    return JsonResponse({"message": "This is the playlist API."})
