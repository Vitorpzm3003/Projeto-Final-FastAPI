from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import pegar_sessao
from main import bcrypt_context
from schemas import UsuarioSchema
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def home():
    """
    Essa é a rota padrão de autenticação
    """
    return {"mensage": "Você acesso a rota de autenticação", "auth":False}

@auth_router.post("/create")
async def create(usuarioSchema: UsuarioSchema, session:Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email==usuarioSchema.email).first()
    if usuario:
        # caso tenha um usuario com este email
        raise HTTPException(status_code=400, detail="Este email já esta em uso") 
    else:
        # caso novo usuario
        senha_criptografada = bcrypt_context.hash(usuarioSchema.senha)
        newUser = Usuario(usuarioSchema.nome,usuarioSchema.email,senha_criptografada, usuarioSchema.status, usuarioSchema.nivel)
        session.add(newUser)
        session.commit()
        return{f"Usuario cadastrado {usuarioSchema.email}"}
