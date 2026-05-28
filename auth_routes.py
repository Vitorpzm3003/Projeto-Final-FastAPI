from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, ALGORITHM, ACCES_TOKEN_EXPIRE, SECRET_KEY
from schemas import UsuarioSchema, loginSchema
from sqlalchemy.orm import Session
from jose import jwt,JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(id_usuario, duracao_token = timedelta(minutes = ACCES_TOKEN_EXPIRE)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dicionario_info = {"sub": str(id_usuario), "exp": data_expiracao}
    jwt_codificado = jwt.encode(dicionario_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado

def auth_user(email,senha,session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    
    return usuario


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
    usuario = auth_user(login_schema.email, login_schema.senha, session)

    if not usuario:
        raise HTTPException(status_code=400, detail="usuario nao encontrado ou credenciais invalidas")
    else:
        access_token = create_token(usuario.id)
        refresh_token = create_token(usuario.id, duracao_token=timedelta(days=7))
        return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer"
            }
    
@auth_router.post("/login-form")
async def loginForm(dados_form: OAuth2PasswordRequestForm = Depends() ,session:Session = Depends(pegar_sessao)):
    usuario = auth_user(dados_form.username, dados_form.password, session)

    if not usuario:
        raise HTTPException(status_code=400, detail="usuario nao encontrado ou credenciais invalidas")
    else:
        access_token = create_token(usuario.id)
        return {
                "access_token": access_token,
                "token_type": "Bearer"
            }


@auth_router.get("/refresh")
async def Refresh(usuario: Usuario = Depends(verificar_token)):
    access_token = create_token(usuario.id)
    return{
        "access_token": access_token,
        "token_type": "Bearer"
    }

