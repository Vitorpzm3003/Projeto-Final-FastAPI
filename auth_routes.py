from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, ALGORITHM, ACCES_TOKEN_EXPIRE, SECRET_KEY
from schemas import UsuarioSchema, loginSchema, UsuarioUpdate
from sqlalchemy.orm import Session
from jose import jwt,JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(id_usuario, nivel: bool, duracao_token = timedelta(minutes = ACCES_TOKEN_EXPIRE)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dicionario_info = {"sub": str(id_usuario), "exp": data_expiracao, "nivel": nivel}
    jwt_codificado = jwt.encode(dicionario_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado

def auth_user(email,senha,session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    
    return usuario




@auth_router.post("/register")
async def create(usuarioSchema: UsuarioSchema, session:Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email==usuarioSchema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Este email já esta em uso") 
    else:
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
        access_token = create_token(usuario.id, usuario.nivel)
        refresh_token = create_token(usuario.id, usuario.nivel, duracao_token=timedelta(days=7))
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
        access_token = create_token(usuario.id, usuario.nivel)
        return {
                "access_token": access_token,
                "token_type": "Bearer"
            }


@auth_router.post("/refresh")
async def Refresh(usuario: Usuario = Depends(verificar_token)):
    access_token = create_token(usuario.id, usuario.nivel)
    return{
        "access_token": access_token,
        "token_type": "Bearer"
    }

@auth_router.get("/users")
async def get_users(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.nivel:
        raise HTTPException(status_code=401, detail="Acesso negado")
    users = session.query(Usuario).all()
    return {"usuarios": [{"id": u.id, "nome": u.nome, "email": u.email, "status": u.status, "nivel": u.nivel} for u in users]}

@auth_router.delete("/users/{id_usuario}")
async def delete_user(id_usuario: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.nivel:
        raise HTTPException(status_code=401, detail="Acesso negado")
    if usuario.id == id_usuario:
        raise HTTPException(status_code=400, detail="Não pode excluir a si mesmo")
    
    user = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")
        
    session.delete(user)
    session.commit()
    return {"mensagem": "Usuário removido com sucesso"}

@auth_router.patch("/users/{id_usuario}")
async def update_user(id_usuario: int, updates: UsuarioUpdate, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.nivel:
        raise HTTPException(status_code=401, detail="Acesso negado")
        
    user = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")
        
    if updates.nome is not None:
        user.nome = updates.nome
    if updates.email is not None:
        user.email = updates.email
    if updates.nivel is not None:
        user.nivel = updates.nivel
    if updates.senha:
        user.senha = bcrypt_context.hash(updates.senha)
        
    session.commit()
    return {"mensagem": "Usuário atualizado com sucesso"}

