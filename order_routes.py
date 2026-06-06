from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import OrderSchema, ItemPedidoSchema, PedidoStatusUpdate
from models import Pedido, Usuario, ItemPedido

order_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def List(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if usuario.nivel:
        pedidos = session.query(Pedido).all()
    else:
        pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
    return{
        "pedidos":pedidos
    }

@order_router.post("/")
async def createOrder(order_schema: OrderSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    user_id = order_schema.usuario if (usuario.nivel and order_schema.usuario) else usuario.id
    newOrder = Pedido(usuario=user_id)
    session.add(newOrder)
    session.flush()
    
    if order_schema.itens:
        for item in order_schema.itens:
            item_pedido = ItemPedido(quantidade=item.quantidade, tipo=item.tipo, precoUnitario=item.precoUnitario, pedido=newOrder.id)
            session.add(item_pedido)
        
        session.flush()
        newOrder.calc_preco()
        
    session.commit()
    return {"mensagem": "Pedido criado com sucesso", "id": newOrder.id}

@order_router.get("/{id_pedido}")
async def getOrder(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="pedido nao encontrado")
    if not usuario.nivel and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Acesso negado")
    return{
        "quantidade_items": len(pedido.itens),
        "pedido": pedido
    }

@order_router.patch("/{id_pedido}/status")
async def update_status(id_pedido:int, status_update: PedidoStatusUpdate, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="pedido nao encontrado")
    if not usuario.nivel and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Acesso negado")
        
    novo_status = status_update.status.upper()
    if novo_status not in ["CANCELADO", "FINALIZADO"]:
        raise HTTPException(status_code=400, detail="status invalido")
        
    pedido.status = novo_status
    if novo_status == "FINALIZADO" and status_update.forma_pagamento:
        pedido.forma_pagamento = status_update.forma_pagamento
        
    session.commit()
    return {
        "mensagem": f"O pedido {pedido.id} foi atualizado para {pedido.status} com sucesso",
        "pedido": pedido
    }

@order_router.delete("/{id_pedido}")
async def deleteOrder(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.nivel:
        raise HTTPException(status_code=401, detail="Acesso negado")
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    session.delete(pedido)
    session.commit()
    return {"mensagem": "Pedido deletado com sucesso"}

@order_router.post("/{id_pedido}/items")
async def add(id_pedido: int, item: ItemPedidoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="pedido inexistente")
    if not usuario.nivel and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Acesso negado")
        
    if pedido.status != "PENDENTE":
        raise HTTPException(status_code=400, detail="Nao e possivel adicionar itens a pedidos ja finalizados ou cancelados")

    item_pedido = ItemPedido(item.quantidade, item.tipo, item.precoUnitario, id_pedido)
    session.add(item_pedido)
    session.commit()
    session.refresh(pedido)
    pedido.calc_preco()
    session.commit()
    return{
        "mensagem": "Item criado com sucesso",
        "item_id": item_pedido.id,
        "preco": pedido.preco
    }

@order_router.delete("/{id_pedido}/items/{id_item_pedido}")
async def remove(id_pedido: int, id_item_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido, ItemPedido.pedido == id_pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="item inexistente no pedido selecionado")
        
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="pedido inexistente")
        
    if not usuario.nivel and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Acesso negado")
        
    if pedido.status != "PENDENTE":
        raise HTTPException(status_code=400, detail="Nao e possivel remover itens de pedidos ja finalizados ou cancelados")
        
    session.delete(item_pedido)
    session.commit()
    
    session.refresh(pedido)
    pedido.calc_preco()
    session.commit()
    
    return{
        "mensagem": "Item removido com sucesso",
        "preco_pedido": pedido.preco,
        "pedido": id_pedido
    }