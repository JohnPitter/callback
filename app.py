from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import requests

app = FastAPI()

# Configurações do Spotify
CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"
REDIRECT_URI = (
    "http://localhost:8000/callback"  # A URL para onde o Spotify irá redirecionar
)
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"


# Rota inicial que retorna status 200 e a mensagem "Hello World"
@app.get("/")
def read_root():
    return JSONResponse(content={"message": "Bem vindo ao Callback"}, status_code=200)


# Rota inicial para redirecionar o usuário ao Spotify para autenticação
@app.get("/login")
def login():
    scopes = "user-read-private user-read-email user-modify-playback-state streaming"
    auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&scope={scopes}&redirect_uri={REDIRECT_URI}"
    return RedirectResponse(auth_url)


# Rota de callback onde o Spotify redireciona após o login
@app.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")

    if not code:
        return JSONResponse({"error": "Authorization code not found"}, status_code=400)

    # Trocar o código de autorização pelo token de acesso
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

    # Verificar se a resposta foi bem sucedida
    if token_response.status_code != 200:
        return JSONResponse(
            {"error": "Failed to get access token", "details": token_response.content},
            status_code=400,
        )

    # Obter o token de acesso
    token_json = token_response.json()
    access_token = token_json.get("access_token")

    # Retornar o token de acesso ou fazer algo com ele
    return JSONResponse({"access_token": access_token})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
