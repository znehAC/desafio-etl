from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from marshmallow import Schema, fields

Base = declarative_base()

class Proposicao(Base):
    __tablename__ = 'proposicao'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String)
    presentationDate = Column(DateTime, nullable=True)
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
    createdAt = Column(DateTime, nullable=True)
    description = Column(String)
    local = Column(String)
    propositionId = Column(Integer, ForeignKey('proposicao.id'))


class ProposicaoSchema(Schema):
  author = fields.Str(allow_none=True)
  presentationDate = fields.DateTime(allow_none=True, format="%Y-%m-%d")
  ementa = fields.Str()
  regime = fields.Str()
  situation = fields.Str()
  propositionType = fields.Str()
  number = fields.Str()
  year = fields.Int(allow_none=True)
  city = fields.Str(default="Belo Horizonte")
  state = fields.Str(default="Minas Gerais")

class TramitacaoSchema(Schema):
  createdAt = fields.DateTime(allow_none=True, format="%Y-%m-%d")
  description = fields.Str()
  local = fields.Str()
  propositionId = fields.Int()