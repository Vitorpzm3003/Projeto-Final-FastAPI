from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import pegar_sessao
from main import bcrypt_context
from schemas import UsuarioSchema, loginSchema
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(email):
    token = f"puR3d3B4taT45{email}"
    return token


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


@auth_router.post("/login")
async def login(login_schema: loginSchema ,session:Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email==login_schema.email).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="usuario nao encontrado")
    else:
        access_token = create_token(usuario.id)
        return {
                "access_token": access_token,
                "token_type": "Bearer"
            }
    