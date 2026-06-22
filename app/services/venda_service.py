from datetime import datetime, date
from typing import List, Optional

from app.models.transacao.venda.venda import Venda
from app.models.transacao.item_transacao import ItemTransacao
from app.models.estoque.exemplar import Exemplar
from app.models.estoque.midia_fisica import MidiaFisica
from app.models.estoque.midia_digital import MidiaDigital
from app.models.catalogo.catalogo import Catalogo
from app.models.enums import StatusSituacao, StatusVenda
from app.repository.interface.venda_repository_interface import VendaRepositoryInterface
from app.repository.interface.estoque_repository_interface import EstoqueRepositoryInterface
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface


class VendaService:
    """
    Service layer for Venda operations
    Handles business logic for sales operations
    """

    def __init__(
        self,
        venda_repository: VendaRepositoryInterface,
        estoque_repository: EstoqueRepositoryInterface,
        catalogo_repository: CatalogoRepositoryInterface
    ):
        self.venda_repository = venda_repository
        self.estoque_repository = estoque_repository
        self.catalogo_repository = catalogo_repository

    def get_by_id(self, id: int) -> Optional[Venda]:
        """Get venda by ID"""
        return self.venda_repository.get_by_id(id)

    def get_by_cliente(self, cliente_id: int) -> List[Venda]:
        """Get all vendas for a specific cliente"""
        return self.venda_repository.get_by_cliente(cliente_id)

    def find_exemplar_disponivel_venda(self, id_jogo: int, tipo_midia: str) -> Optional[Exemplar]:
        """Find available exemplar for sale based on game and media type"""
        catalogo = self.catalogo_repository.get_by_id(id_jogo)
        if not catalogo:
            return None

        if tipo_midia == 'DIGITAL':
            # For digital media, check if there's an available digital copy
            digitais = self.estoque_repository.get_exemplares_by_catalogo(id_jogo)
            for digital in digitais:
                if isinstance(digital, MidiaDigital):
                    # Check if this digital copy is not already sold
                    # This is simplified - in a real system you'd check transaction history
                    return digital
        elif tipo_midia == 'FISICA':
            # For physical media, find an available physical copy
            fisicas = self.estoque_repository.get_exemplares_by_catalogo(id_jogo)
            for fisica in fisicas:
                if isinstance(fisica, MidiaFisica):
                    # Check if this physical copy is available
                    situacao = getattr(fisica.situacao, 'value', fisica.situacao) if hasattr(fisica, 'situacao') else None
                    if situacao == 'DISPONIVEL' or situacao is None:
                        return fisica
        
        return None

    def criar_venda(
        self,
        cliente_id: int,
        id_jogo: int,
        tipo_midia: str
    ) -> tuple[Optional[Venda], Optional[str]]:
        """
        Create a new venda
        Returns (venda, error_message)
        """
        # Validate catalogo exists and is available for sale
        catalogo = self.catalogo_repository.get_by_id(id_jogo)
        if not catalogo:
            return None, "Jogo não encontrado no catálogo."

        if not catalogo.valor_venda:
            return None, "Este jogo não está disponível para venda."

        # Validate media type
        tipo_midia = tipo_midia.upper()
        if tipo_midia not in ['FISICA', 'DIGITAL']:
            return None, "tipo_midia deve ser FISICA ou DIGITAL."

        # Find available exemplar
        exemplar = self.find_exemplar_disponivel_venda(id_jogo, tipo_midia)
        if not exemplar:
            return None, f"Não há exemplares da mídia {tipo_midia} disponíveis para este jogo."

        # Create venda
        valor_total = catalogo.valor_venda
        nova_venda = Venda(
            valor_total=valor_total,
            status='FINALIZADA',
            data_transacao=datetime.utcnow(),
            data_confirmacao=date.today()
        )
        # set foreign key id explicitly (repository/create will persist this)
        nova_venda.id_cliente = cliente_id

        venda_criada = self.venda_repository.create(nova_venda)
        if not venda_criada:
            return None, "Erro ao criar venda."

        # Ensure the foreign key to cliente is persisted. Some constructors
        # and polymorphic mappings may not persist the id set on the Python
        # instance, so update explicitly if needed.
        if getattr(venda_criada, 'id_cliente', None) != cliente_id:
            venda_criada.id_cliente = cliente_id
            venda_criada = self.venda_repository.update(venda_criada)

        # Create item transacao
        # ItemTransacao constructor accepts related objects (transacao, exemplar)
        item = ItemTransacao(
            transacao=venda_criada,
            exemplar=exemplar,
            valor_unitario=valor_total
        )

        item_criado = self.venda_repository.create_item_transacao(item)
        if not item_criado:
            return None, "Erro ao vincular exemplar à venda."

        # Update exemplar situation
        if isinstance(exemplar, MidiaFisica):
            exemplar.situacao = 'VENDIDO'
            self.estoque_repository.update_midia_fisica(exemplar)

        return venda_criada, None

    def estornar_venda(self, venda_id: int, cliente_id: int) -> tuple[bool, Optional[str]]:
        """
        Cancel/estornar a venda
        Returns (success, error_message)
        """
        venda = self.venda_repository.get_by_id(venda_id)
        if not venda:
            return False, "Venda não encontrada."

        if venda.id_cliente != cliente_id:
            return False, "Venda não pertence a este cliente."

        venda_status = getattr(venda.status, 'value', venda.status)
        if venda_status == 'ESTORNADA':
            return False, "Esta venda já foi estornada."

        # Update venda status
        venda.status = StatusVenda.ESTORNADA.value
        self.venda_repository.update(venda)

        # Restore exemplar availability
        item = self.venda_repository.get_item_by_transacao(venda_id)
        if item:
            exemplar = self.estoque_repository.get_exemplar_by_id(item.id_exemplar)
            if exemplar and isinstance(exemplar, MidiaFisica):
                exemplar.situacao = StatusSituacao.DISPONIVEL.value
                self.estoque_repository.update_midia_fisica(exemplar)

        return True, None

    def serialize_venda(self, venda: Venda) -> dict:
        """Serialize venda to dict"""
        return {
            "id_transacao": venda.id,
            "data_transacao": venda.data_transacao.isoformat() if venda.data_transacao else None,
            "valor_total": float(venda.valor_total) if venda.valor_total else None,
            "status_venda": venda.status,
            "id_cliente": venda.id_cliente,
            "data_confirmacao": venda.data_confirmacao.isoformat() if venda.data_confirmacao else None
        }
