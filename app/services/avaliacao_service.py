from typing import List, Optional
from app.models import Avaliacao, Aluguel, Venda
from app.models.enums import StatusAluguel, StatusVenda
from app.repository.interface.usuario_repository_interface import UsuarioRepositoryInterface
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface

class AvaliacaoService:
    """
    Service layer for Avaliacao operations.
    """

    def __init__(self, usuario_repo: UsuarioRepositoryInterface, catalogo_repo: CatalogoRepositoryInterface):
        self.usuario_repo = usuario_repo
        self.catalogo_repo = catalogo_repo

    def criar_avaliacao(self, id_cliente: int, id_transacao: int, nota: int, comentario: Optional[str] = None) -> Avaliacao:
        """
        Cria uma nova avaliação para uma transação, validando as regras de negócio.
        """
        if not (1 <= nota <= 5):
            raise ValueError("A nota da avaliação deve ser entre 1 e 5.")

        transacao = self.usuario_repo.get_transacao_by_id(id_transacao) # Supondo que este método exista
        if not transacao:
            raise ValueError("Transação não encontrada.")
        
        if transacao.id_cliente != id_cliente:
            raise PermissionError("O cliente não tem permissão para avaliar esta transação.")

        if isinstance(transacao, Aluguel) and transacao.status != StatusAluguel.FINALIZADO.value:
            raise ValueError("Só é possível avaliar aluguéis finalizados.")
        
        if isinstance(transacao, Venda) and transacao.status != StatusVenda.FINALIZADA.value:
            raise ValueError("Só é possível avaliar vendas finalizadas.")

        if transacao.avaliacao:
            raise ValueError("Esta transação já foi avaliada.")

        nova_avaliacao = Avaliacao(
            id_transacao=id_transacao,
            nota=nota,
            comentario=comentario
        )
        
        return self.usuario_repo.create_avaliacao(nova_avaliacao) # Supondo que este método exista

    def get_avaliacoes_por_cliente(self, id_cliente: int) -> List[Avaliacao]:
        """Retorna todas as avaliações feitas por um cliente."""
        return self.usuario_repo.get_avaliacoes_by_cliente(id_cliente) # Supondo que este método exista

    def get_avaliacoes_por_jogo(self, id_catalogo: int) -> List[Avaliacao]:
        """Retorna todas as avaliações de um determinado jogo."""
        return self.catalogo_repo.get_avaliacoes_by_jogo(id_catalogo) # Supondo que este método exista
