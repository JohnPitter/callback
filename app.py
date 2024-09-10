from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import requests

app = FastAPI()

# Replace these with your Spotify app's credentials
CLIENT_ID = "4f472f06012b4431b32c2c8103643055"
CLIENT_SECRET = "848a03c4b0f54153989835786ed74d94"
REDIRECT_URI = "https://callback-jals.onrender.com/callback"

# Authorization URL for Spotify
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

# Scopes needed for the app
SCOPES = "user-read-private user-read-email user-modify-playback-state streaming"


@app.get("/")
def login():
    """Redirect the user to Spotify's authorization page."""
    auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&scope={SCOPES}&redirect_uri={REDIRECT_URI}"
    return RedirectResponse(auth_url)


@app.get("/callback")
def callback(request: Request, code: str = None, error: str = None):
    """Callback endpoint to capture the authorization code and exchange it for an access token."""
    if error:
        return JSONResponse({"error": error})

    if code:
        # Exchange authorization code for access token
        token_response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_response.status_code != 200:
            return {"error": "Failed to get access token"}

        # Extract the token from the response
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        # Redirect back to the frontend with the access token (could also return it directly)
        frontend_url = f"https://johnpitter.github.io/player/index.html?access_token={access_token}"
        return RedirectResponse(frontend_url)
    else:
        return {"error": "Authorization code not found"}


@app.get("/user_profile")
def get_user_profile(access_token: str):
    """Fetch user profile information using the access token."""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)

    if response.status_code != 200:
        return {"error": "Failed to fetch user profile"}

    return response.json()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
