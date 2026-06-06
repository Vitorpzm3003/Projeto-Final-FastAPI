from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import ProdutoSchema
from models import Produto, Usuario

produto_router = APIRouter(prefix="/produtos", tags=["produtos"], dependencies=[Depends(verificar_token)])

@produto_router.get("/")
async def get_produtos(session: Session = Depends(pegar_sessao)):
    produtos = session.query(Produto).filter(Produto.ativo == True).all()
    return {"produtos": produtos}

@produto_router.post("/")
async def create_produto(produto: ProdutoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.nivel:
        raise HTTPException(status_code=401, detail="Acesso negado")
    
    novo_produto = Produto(nome=produto.nome, preco=produto.preco, ativo=produto.ativo)
    session.add(novo_produto)
    session.commit()
    return {"mensagem": "Produto criado com sucesso", "id": novo_produto.id}

@produto_router.delete("/{id_produto}")
async def delete_produto(id_produto: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.nivel:
        raise HTTPException(status_code=401, detail="Acesso negado")
        
    produto = session.query(Produto).filter(Produto.id == id_produto).first()
    if not produto:
        raise HTTPException(status_code=400, detail="Produto não encontrado")
        
    produto.ativo = False # Soft delete
    session.commit()
    return {"mensagem": "Produto removido com sucesso"}
