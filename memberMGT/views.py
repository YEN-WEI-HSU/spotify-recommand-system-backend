from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import response
from requests import Request, post
from django.http import HttpResponseRedirect
from .credentials import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
from .extra import *

class AuthenticationaURL(APIView):
    def get(self, request, format=None):
        scopes = "user-read-private, user-read-email, user-top-read, user-follow-read, user-follow-modify, user-library-read, user-library-modify, playlist-modify-public, playlist-modify-private, playlist-read-private, playlist-read-collaborative, playlist-modify-public, playlist-modify-private,"
        url =Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': SPOTIFY_REDIRECT_URI,
            'client_id': SPOTIFY_CLIENT_ID,
        }).prepare().url
        return HttpResponseRedirect(url)

def spotify_redirect(request, format=None):
    code = request.GET.get("code")
    error = request.GET.get("error")

    if error:
        return error
    
    response = post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }).json()

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
    redirect_url = ""
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
            redirect_url = ""
            return HttpResponseRedirect(redirect_url)
        else:
            redirect_url = ""
            return HttpResponseRedirect(redirect_url)
