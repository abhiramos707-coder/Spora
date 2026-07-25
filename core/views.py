import base64
import requests

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from urllib.parse import urlencode


def home(request):
    return render(request, "home.html")


def spotify_login(request):
    scope = (
        "user-read-private "
        "user-read-email "
        "playlist-modify-public "
        "playlist-modify-private"
    )

    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": scope,
    }

    auth_url = "https://accounts.spotify.com/authorize?" + urlencode(params)
    return redirect(auth_url)


from django.shortcuts import redirect
import requests
import base64

def spotify_callback(request):
    code = request.GET.get("code")

    if not code:
        return HttpResponse("Authorization failed.")

    token_url = "https://accounts.spotify.com/api/token"

    credentials = (
        f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
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
        return HttpResponse(f"Error: {response.text}")

    token_info = response.json()
    access_token = token_info.get("access_token")

    if not access_token:
        return HttpResponse("Failed to get access token.")

    # Store the access token in the session
    request.session["access_token"] = access_token

    # Redirect to the dashboard
    return redirect("dashboard")
def dashboard(request):
    access_token = request.session.get("access_token")

    if not access_token:
        return redirect("spotify_login")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        "https://api.spotify.com/v1/me",
        headers=headers
    )

    if response.status_code != 200:
        return HttpResponse("Failed to fetch Spotify profile.")

    profile = response.json()

    context = {
        "name": profile.get("display_name"),
        "email": profile.get("email"),
        "country": profile.get("country"),
        "profile_image": (
            profile["images"][0]["url"]
            if profile.get("images")
            else None
        ),
    }

    return render(request, "dashboard.html", context)
    # Show Spotify's response if token exchange fails
   
    if response.status_code != 200:
        return HttpResponse(
            f"<pre>{response.status_code}\n\n{response.text}</pre>"
        )

    token_info = response.json()

    access_token = token_info.get("access_token")

    if not access_token:
        return HttpResponse(f"<pre>{token_info}</pre>")

    request.session["access_token"] = access_token

    profile_response = requests.get(
        "https://api.spotify.com/v1/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    if profile_response.status_code != 200:
        return HttpResponse(
            f"<pre>{profile_response.status_code}\n\n{profile_response.text}</pre>"
        )

    profile = profile_response.json()

    return HttpResponse(
        f"""
        <h2>🎉 Spotify Connected!</h2>

        <p><strong>Name:</strong> {profile.get("display_name")}</p>
        <p><strong>Email:</strong> {profile.get("email")}</p>
        <p><strong>Country:</strong> {profile.get("country")}</p>
        <p><strong>Spotify ID:</strong> {profile.get("id")}</p>
        """
    )