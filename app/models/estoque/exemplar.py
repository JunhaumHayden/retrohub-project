from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base_model import Base
from app.models.enums import StatusSituacao

class Exemplar(Base):
    __tablename__ = 'exemplares'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_catalogo = Column(Integer, ForeignKey('catalogo.id'), nullable=False)
    tipo_midia = Column(String(50), nullable=False)
    situacao = Column(Enum(StatusSituacao), default=StatusSituacao.DISPONIVEL)

    catalogo = relationship("Catalogo", back_populates="exemplares")

    __mapper_args__ = {
        'polymorphic_identity': 'exemplar',
        'polymorphic_on': tipo_midia
    }

    def set_situacao(self, situacao: str):
        self.situacao = StatusSituacao(situacao)
