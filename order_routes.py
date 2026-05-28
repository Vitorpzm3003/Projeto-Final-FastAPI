from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies import pegar_sessao
from schemas import OrderSchema
from models import Pedido

order_router = APIRouter(prefix="/orders", tags=["orders"])

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