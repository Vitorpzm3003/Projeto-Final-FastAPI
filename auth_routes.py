from fastapi import APIRouter, Depends
from models import Usuario
from dependencies import pegar_sessao

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def home():
    """
    Essa é a rota padrão de autenticação
    """
    return {"mensage": "Você acesso a rota de autenticação", "auth":False}

@auth_router.post("/create")
async def create(email: str, senha: str, nome: str, session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if usuario:
        # caso tenha um usuario com este email
        return {"já existe um usuario com esse email"}
    else:
        # caso novo usuario
        newUser = Usuario(nome,email,senha)
        session.add(newUser)
        session.commit()
        return{"Usuario cadastrado"}
