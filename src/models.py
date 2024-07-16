from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Proposicao(Base):
    __tablename__ = 'proposicao'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String)
    presentationDate = Column(DateTime)
    ementa = Column(String)
    regime = Column(String)
    situation = Column(String)
    propositionType = Column(String)
    number = Column(String)
    year = Column(Integer)
    city = Column(String, default="Belo Horizonte")
    state = Column(String, default="Minas Gerais")

    tramitacoes = relationship('Tramitacao', backref='proposicao')

class Tramitacao(Base):
    __tablename__ = 'tramitacao'
    id = Column(Integer, primary_key=True, autoincrement=True)
    createdAt = Column(DateTime)
    description = Column(String)
    local = Column(String)
    propositionId = Column(Integer, ForeignKey('proposicao.id'))