from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import OrderSchema, ItemPedidoSchema
from models import Pedido, Usuario, ItemPedido

order_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def getList():
    """
    rota padrao de pedidos
    """
    return {"mensagem": "Lista de pedidos"}

@order_router.post("/order")
async def createOrder(order_schema: OrderSchema, session: Session = Depends(pegar_sessao)):
    newOrder = Pedido(usuario=order_schema.usuario)
    session.add(newOrder)
    session.commit()
    return {f"Pedido criado com sucesso. ID do pedido: {newOrder.id}"}

@order_router.post("/order/cancelar/{id_pedido}")
async def cancel(id_pedido:int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):

    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="pedido nao encontrado")
    if not usuario.nivel and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Acesso negado")
    pedido.status = "CANCELADO"
    session.commit()
    return {
        "mensagem": f"O pedido {pedido.id} cancelado com sucesso",
        "pedido": pedido
    }

@order_router.get("/list")
async def Listar(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if usuario.nivel == False:
        raise HTTPException(status_code=401, detail="Acesso negado")
    else:
        pedidos = session.query(Pedido).all()
        return{
            "pedidos":pedidos
        }

@order_router.post("/order/addItem/{id_pedido}")
async def add(id_pedido: int, item: ItemPedidoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="pedido inexistente")
    if not usuario.nivel and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Acesso negado")
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
    
