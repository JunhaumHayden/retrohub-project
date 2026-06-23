from datetime import date
from typing import Optional
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base_model import Base


class Avaliacao(Base):
    __tablename__ = 'avaliacoes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_transacao = Column(Integer, ForeignKey('transacoes.id'), nullable=False)
    nota = Column(Integer)
    comentario = Column(String(500))
    data_avaliacao = Column(Date, default=date.today)
    
    transacao = relationship("Transacao", back_populates="avaliacao")
