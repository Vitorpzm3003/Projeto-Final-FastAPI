from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def authenticate():
    """
    Essa é a rota padrão de autenticação
    """
    return {"mensage": "Você acesso a rota de autenticação", "auth":False}