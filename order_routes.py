from fastapi import APIRouter

order_router = APIRouter(prefix="/order", tags=["order"])

@order_router.get("/")
async def getList():
    """
    Essa é a rota padrao de pedidos.  Todas as rotas de orders precisam de autenticação
    """
    return {"mensagem": "Lista de pedidos"}

