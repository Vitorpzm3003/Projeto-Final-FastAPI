from pydantic import BaseModel
from typing import Optional

class UsuarioSchema(BaseModel):
    nome:str
    email:str
    senha:str
    status: Optional[bool]
    nivel: Optional[bool]

    class Config:
        from_attributes = True


class OrderSchema(BaseModel):
    usuario: int
    
    class Config:
        from_attributes = True
    

class loginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True