from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import response
from requests import Request, post, get
from django.http import HttpResponseRedirect, JsonResponse
from .services import *
import os
from dotenv import load_dotenv
from .models import Token
from .services import generate_jwt
from django.utils import timezone
import datetime
from datetime import timedelta

load_dotenv()  # Load environment variables from .env file

class test(APIView):
    def get(self, request, format=None):
        return response.Response({"message": "Hello, world!"}, status=status.HTTP_200_OK)

class AuthenticationaURL(APIView):
    def get(self, request, format=None):
        scopes = " ".join([
            "user-read-private",
            "user-read-email",
            "user-top-read",
            "user-follow-read",
            "user-follow-modify",
            "user-library-read",
            "user-library-modify",
            "playlist-modify-public",
            "playlist-modify-private",
            "playlist-read-private",
            "playlist-read-collaborative",
        ])
        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': os.getenv("SPOTIFY_REDIRECT_URI"),  # Use environment variable for redirect URI
            'client_id': os.getenv("SPOTIFY_CLIENT_ID"),  # Use environment variable for client ID
        }).prepare().url
        print(f"Redirecting to Spotify authorization URL: {os.getenv('SPOTIFY_REDIRECT_URI')}")
        print(f"Client ID: {os.getenv('SPOTIFY_CLIENT_ID')}")
        print(f"Authorization URL: {url}")
        return HttpResponseRedirect(url)

def spotify_redirect(request, format=None):
    request.session.flush()
    code = request.GET.get("code")
    error = request.GET.get("error")

    print(f"[Callback] Code: {code}")
    print(f"[Callback] Error: {error}")

    if error:
        return error

    token_response = post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv('SPOTIFY_REDIRECT_URI'),
        "client_id": os.getenv('SPOTIFY_CLIENT_ID'),
        "client_secret": os.getenv('SPOTIFY_CLIENT_SECRET'),
    })
    print("[DEBUG] SPOTIFY_REDIRECT_URI used for token request:", os.getenv('SPOTIFY_REDIRECT_URI'))

    print("Spotify Authorization URL:", token_response)
    print("Token Response Status:", token_response.status_code)
    print("Token Response Body:", token_response.text)
    response = token_response.json()

    access_token = response.get("access_token")
    refresh_token = response.get("refresh_token")
    expires_in = response.get("expires_in")
    token_type = response.get("token_type")

    authKey = request.session.session_key
    if not request.session.exists(authKey):
        request.session.create()
        authKey = request.session.session_key

    userInfo_response = get("https://api.spotify.com/v1/me", headers={
        "Authorization": f"Bearer {access_token}"
    })
    print(f"[DEBUG] UserInfo_response URL: {userInfo_response.url}")
    print(f"[DEBUG] User Info Response Status: {userInfo_response.status_code}")
    print(f"[DEBUG] User Info Response Body: {userInfo_response.text}")
    userInfo = userInfo_response.json()
    print(f"[DEBUG] User Info Response: {userInfo}")
    spotify_id = userInfo.get("id")
    spotify_name = userInfo.get("display_name")
    # userName = "test_user"  # Placeholder for user name, replace with actual user info retrieval

    jwt_token = generate_jwt(spotify_id, spotify_name)
    jwt_expires_in = timezone.now() + timedelta(days=7)

    create_or_update_tokens(
        session_id=spotify_id,
        spotify_name=spotify_name,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        token_type=token_type,
        jwt_token=jwt_token,
        jwt_expires_in=jwt_expires_in
    )

    redirect_url = os.getenv("FRONTEND_URL")
    print(f"Redirecting to: {redirect_url}")
    redirect_url_with_token = f"{redirect_url}?token={jwt_token}"

    return HttpResponseRedirect(redirect_url_with_token)

class CheckAuthentication(APIView):
    def get(self, request, format=None):
        key = self.request.session.session_key
        if not self.request.session.exists(key):
            self.request.session.create()
            key = self.request.session.session_key

        auth_status = is_spotify_authenticated(key)

        if auth_status:
            redirect_url = os.getenv("FRONTEND_URL")  # Redirect to the frontend URL
            print(f"User is authenticated, redirecting to: {redirect_url}")
            return HttpResponseRedirect(redirect_url)
        else:
            redirect_url = os.getenv("FRONTEND_LOGIN_URL")
            print(f"User is not authenticated, redirecting to: {redirect_url}")
            return HttpResponseRedirect(redirect_url)

def get_current_user_playlists(request):
    jwt_token = request.GET.get('token')
    if not jwt_token:
        print("No JWT token provided.")
        return None
    
    tokens = check_jwt_tokens(jwt_token)
    if not tokens:
        print("No valid tokens found for the provided JWT token.")
        return None
    
    headers = {
        "Authorization": f"Bearer {tokens.access_token}"
    }
    response = get('https://api.spotify.com/v1/me/playlists?limit=5', headers=headers)
    if response.status_code != 200:
        print("Spotify API error:", response.status_code, response.text)
        return JsonResponse({'error': 'Spotify API error', 'detail': response.text}, status=response.status_code)

    return JsonResponse(response.json(), safe=False)