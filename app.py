from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# Um dicionário em memória para armazenar o token
# (Em produção, você pode armazenar em um banco de dados ou outro local persistente)
tokens = {}


# Rota de callback onde o Spotify redireciona após o login
class TokenData(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


@app.post("/callback")
def store_token(token_data: TokenData):
    # Armazenar o token na memória (pode ser banco de dados, etc.)
    tokens["access_token"] = token_data.access_token
    tokens["token_type"] = token_data.token_type
    tokens["expires_in"] = token_data.expires_in

    return {"message": "Token armazenado com sucesso", "token_data": token_data}


# Rota para retornar o código de callback armazenado
@app.get("/code")
def get_code():
    if tokens:
        return JSONResponse({"callback_code": tokens}, status_code=200)
    else:
        return JSONResponse({"error": "No callback code stored"}, status_code=404)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
