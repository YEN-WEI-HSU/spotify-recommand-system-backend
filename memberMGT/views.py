from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import response
from requests import Request, post
from django.http import HttpResponseRedirect
from .services import *
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class test(APIView):
    def get(self, request, format=None):
        return response.Response({"message": "Hello, world!"}, status=status.HTTP_200_OK)

class AuthenticationaURL(APIView):
    def get(self, request, format=None):
        scopes = "user-read-private, user-read-email, user-top-read, user-follow-read, user-follow-modify, user-library-read, user-library-modify, playlist-modify-public, playlist-modify-private, playlist-read-private, playlist-read-collaborative, playlist-modify-public, playlist-modify-private,"
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
    code = request.GET.get("code")
    error = request.GET.get("error")

    print(f"[Callback] Code: {code}")
    print(f"[Callback] Error: {error}")

    if error:
        return error
    
    # response = post("https://accounts.spotify.com/api/token", data={
    #     "grant_type": "authorization_code",
    #     "code": code,
    #     "redirect_uri": SPOTIFY_REDIRECT_URI,
    #     "client_id": SPOTIFY_CLIENT_ID,
    #     "client_secret": SPOTIFY_CLIENT_SECRET,
    # }).json()

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

    create_or_update_tokens(
        session_id=authKey,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        token_type=token_type
    )

    # Create a redirect url to the current song details
    redirect_url = os.getenv("FRONTEND_URL")  #.env / gitignore
    print(f"Redirecting to: {redirect_url}")
    return HttpResponseRedirect(redirect_url)

# Checking whether the user has been authenticated by spotify
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
