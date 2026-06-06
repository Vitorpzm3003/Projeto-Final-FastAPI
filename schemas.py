from pydantic import BaseModel
from typing import Optional, List

class UsuarioSchema(BaseModel):
    nome:str
    email:str
    senha:str
    status: Optional[bool]
    nivel: Optional[bool]

    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    nivel: Optional[bool] = None

    class Config:
        from_attributes = True

class loginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True

class ItemPedidoSchema(BaseModel):
    quantidade: int
    tipo: str
    precoUnitario: float

    class Config:
        from_attributes = True

class OrderSchema(BaseModel):
    usuario: Optional[int] = None
    itens: Optional[List[ItemPedidoSchema]] = []
    
    class Config:
        from_attributes = True
    
class PedidoStatusUpdate(BaseModel):
    status: str
    forma_pagamento: Optional[str] = None

    class Config:
        from_attributes = True

class ProdutoSchema(BaseModel):
    nome: str
    preco: float
    ativo: Optional[bool] = True

    class Config:
        from_attributes = True