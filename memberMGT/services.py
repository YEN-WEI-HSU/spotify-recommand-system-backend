from .models import Token
from django.utils import timezone
from datetime import timedelta
from requests import get, post
import os
from dotenv import load_dotenv
from django.conf import settings
import jwt
import datetime

load_dotenv()

BASE_URL = "https://api.spotify.com/v1/me"

# Check token
def check_tokens(session_id):
    tokens = Token.objects.filter(spotify_id=session_id)
    if tokens:
        return tokens[0]
    else:
        return None

# Check jwt_token
def check_jwt_tokens(jwt_token):
    tokens = Token.objects.filter(jwt_token=jwt_token)
    if tokens:
        return tokens[0]
    else:
        return None
    
# Create and update the token model
def create_or_update_tokens(session_id, spotify_name, access_token, refresh_token, expires_in, token_type, jwt_token, jwt_expires_in):
    print(f"Creating or updating tokens for session: {session_id}")
    print(f"Spotify Name: {spotify_name}")
    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")    
    print(f"Expires In: {expires_in}")
    print(f"Token Type: {token_type}")
    tokens = check_tokens(session_id)
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    # Update tokens if they exist
    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.jwt_token = jwt_token
        tokens.jwt_expires_in = jwt_expires_in
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type', 'jwt_token', 'jwt_expires_in'])

    else:
        tokens = Token(
            spotify_id=session_id,
            spotify_name=spotify_name,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            token_type=token_type,
            jwt_token=jwt_token,
            jwt_expires_in=jwt_expires_in
        )
        tokens.save()

# Check Authentication
def is_spotify_authenticated(session_id):
    tokens = check_tokens(session_id)

    if tokens:
        if tokens.expires_in <= timezone.now():
            pass
        return True
    return False

# Refresh token function
def refresh_token_func(session_id):
    refresh_token = check_tokens(session_id).refresh_token

    response = post("https://accounts.spotify.com/api/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": os.getenv('SPOTIFY_CLIENT_ID'),
        "client_secret": os.getenv('SPOTIFY_CLIENT_SECRET'),
    })
    
    access_token = response.get("access_token")
    expires_in = response.get("expires_in")
    token_type = response.get("token_type")
    
    create_or_update_tokens(
        session_id=session_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        token_type=token_type
    )

def generate_jwt(spotify_id, spotify_name):
    payload = {
        'spotify_id': spotify_id,
        'spotify_name': spotify_name,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token
