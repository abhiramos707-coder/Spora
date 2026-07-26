import base64
import requests

from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect


# ==========================
# Landing Page
# ==========================

def home(request):
    return render(request, "home.html")


# ==========================
# Spotify Login
# ==========================

def spotify_login(request):
    scope = (
        "user-read-private "
        "user-read-email "
        "playlist-modify-public "
        "playlist-modify-private "
        "user-read-recently-played"
    )

    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": scope,
    }

    auth_url = (
        "https://accounts.spotify.com/authorize?"
        + urlencode(params)
    )

    return redirect(auth_url)


# ==========================
# Spotify Callback
# ==========================

def spotify_callback(request):
    code = request.GET.get("code")

    if not code:
        return HttpResponse("Authorization failed.")

    token_url = "https://accounts.spotify.com/api/token"

    credentials = (
        f"{settings.SPOTIFY_CLIENT_ID}:"
        f"{settings.SPOTIFY_CLIENT_SECRET}"
    )

    credentials_b64 = base64.b64encode(
        credentials.encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {credentials_b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
    }

    response = requests.post(
        token_url,
        headers=headers,
        data=data,
    )

    if response.status_code != 200:
        return HttpResponse(response.text)

    token_info = response.json()

    access_token = token_info.get("access_token")

    if not access_token:
        return HttpResponse("Failed to obtain access token.")

    request.session["access_token"] = access_token

    return redirect("dashboard")


# ==========================
# Dashboard
# ==========================

def dashboard(request):

    access_token = request.session.get("access_token")

    if not access_token:
        return redirect("spotify_login")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # ------------------------
    # User Profile
    # ------------------------

    profile_response = requests.get(
        "https://api.spotify.com/v1/me",
        headers=headers,
    )

    if profile_response.status_code != 200:
        return HttpResponse("Failed to fetch Spotify profile.")

    profile = profile_response.json()

    # ------------------------
    # Recently Played
    # ------------------------

    recent_tracks = []

    recent_response = requests.get(
        "https://api.spotify.com/v1/me/player/recently-played?limit=4",
        headers=headers,
    )

    if recent_response.status_code == 200:

        recent_data = recent_response.json()

        for item in recent_data.get("items", []):

            track = item["track"]

            recent_tracks.append({
                "name": track["name"],
                "artist": ", ".join(
                    artist["name"]
                    for artist in track["artists"]
                ),
                "image": track["album"]["images"][0]["url"],
            })

    # ------------------------
    # Context
    # ------------------------

    context = {

        "name": profile.get("display_name"),

        "email": profile.get("email"),

        "country": profile.get("country"),

        "profile_image": (
            profile["images"][0]["url"]
            if profile.get("images")
            else None
        ),

        "recent_tracks": recent_tracks,
    }

    return render(
        request,
        "dashboard.html",
        context,
    )