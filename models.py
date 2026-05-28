from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils.types import ChoiceType



# conexão do banco
db = create_engine("sqlite:///database.db")

# criação da base do banco
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String)
    status = Column("status", Boolean, default= True)
    nivel = Column("nivel", Boolean, default= False)

    def __init__(self, nome, email, senha, status = True, nivel = False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.status = status
        self.nivel = nivel



class Pedido(Base):
    __tablename__ = "pedidos"

    #STATUS_PEDIDOS = (
    #    ("PENDENTE","PENDENTE"),
    #    ("CANCELADO","CANCELADO"),
    #    ("FINALIZADO","FINALIZADO")
    #)

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String)
    usuario = Column("usuario", ForeignKey("usuarios.id"))
    preco = Column("preco", Float, nullable=False)

    def __init__(self,usuario,status="PENDENTE",preco=0):
        self.usuario = usuario
        self.status = status
        self.preco = preco


class ItemPedido(Base):
    __tablename__ = "itemsPedidos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer, nullable=False)
    tipo = Column("tipo", String, nullable=False)
    precoUnitario = Column("precoUnitario", Float, nullable=False)
    pedido = Column("pedido", ForeignKey("pedidos.id"))

    def __init__(self, quantidade,tipo,precoUnitario,pedido):
        self.quantidade = quantidade
        self.tipo = tipo
        self.precoUnitario = precoUnitario
        self.pedido = pedido