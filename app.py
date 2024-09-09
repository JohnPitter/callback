from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse

app = FastAPI()

# Variável global para armazenar o código de callback
callback_code = None

# Configurações do Spotify
CLIENT_ID = "4f472f06012b4431b32c2c8103643055"
CLIENT_SECRET = "848a03c4b0f54153989835786ed74d94"
REDIRECT_URI = "https://callback-jals.onrender.com/callback"  # A URL para onde o Spotify irá redirecionar
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
    global callback_code
    code = request.query_params.get("code")

    if not code:
        return JSONResponse({"error": "Authorization code not found"}, status_code=400)

    # Armazenar o código do callback na variável global
    callback_code = code

    return JSONResponse({"message": "Authorization code received and stored"})


# Rota para retornar o código de callback armazenado
@app.get("/getCode")
def get_code():
    if callback_code:
        return JSONResponse({"callback_code": callback_code}, status_code=200)
    else:
        return JSONResponse({"error": "No callback code stored"}, status_code=404)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
