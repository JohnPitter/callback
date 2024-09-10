from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import base64
import os

# from dotenv import load_dotenv
from urllib.parse import urlencode
import random
import string

app = FastAPI()


# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://johnpitter.github.io"],  # Domínio permitido
    allow_credentials=True,
    allow_methods=[
        "*"
    ],  # Permitir todos os métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)


@app.get("/")
async def read_root():
    return {"message": "CORS is working!"}


# load_dotenv()

spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
spotify_redirect_uri = "https://callback-jals.onrender.com/auth/callback"

access_token = ""


# Função para gerar string aleatória
def generate_random_string(length: int):
    possible = string.ascii_letters + string.digits
    return "".join(random.choice(possible) for i in range(length))


# Rota para login
@app.get("/auth/login")
async def login():
    scope = "streaming user-read-email user-read-private"
    state = generate_random_string(16)

    auth_query_parameters = {
        "response_type": "code",
        "client_id": spotify_client_id,
        "scope": scope,
        "redirect_uri": spotify_redirect_uri,
        "state": state,
    }

    url = "https://accounts.spotify.com/authorize/?" + urlencode(auth_query_parameters)
    return RedirectResponse(url=url)


# Rota de callback
@app.get("/auth/callback")
async def callback(request: Request):
    global access_token
    code = request.query_params.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    auth_options = {
        "url": "https://accounts.spotify.com/api/token",
        "data": {
            "code": code,
            "redirect_uri": spotify_redirect_uri,
            "grant_type": "authorization_code",
        },
        "headers": {
            "Authorization": "Basic "
            + base64.b64encode(
                f"{spotify_client_id}:{spotify_client_secret}".encode()
            ).decode(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
    }

    response = requests.post(
        auth_options["url"], data=auth_options["data"], headers=auth_options["headers"]
    )

    if response.status_code == 200:
        body = response.json()
        access_token = body.get("access_token", "")
        return RedirectResponse(url="https://johnpitter.github.io/player")
    else:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to retrieve access token"
        )


# Rota para obter o token
@app.get("/auth/token")
async def get_token():
    global access_token
    return {"access_token": access_token}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
