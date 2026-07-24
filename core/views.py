

# Create your views here.

from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect
from urllib.parse import urlencode
def home(request):
    return render(request, 'home.html')
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