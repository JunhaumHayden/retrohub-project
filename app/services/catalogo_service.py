from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.models.catalogo.catalogo import Catalogo
from app.models.estoque.midia_digital import MidiaDigital
from app.models.estoque.midia_fisica import MidiaFisica
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface
from app.models.enums import StatusCatalogo


class CatalogoService:
    """
    Service layer for Catalogo operations
    Handles business logic and validation
    """

    def __init__(self, repository: CatalogoRepositoryInterface):
        self.repository = repository

    def list_all(self, ativo: Optional[bool] = None) -> List[Catalogo]:
        """List all catalog items, optionally filtered by active status"""
        catalogos = self.repository.list_all()
        
        if ativo is not None:
            # Convert ativo boolean to situacao string
            situacao_filtro = StatusCatalogo.DISPONIVEL.value if ativo else StatusCatalogo.INDISPONIVEL.value
            catalogos = [c for c in catalogos if c.situacao == situacao_filtro]
        
        return catalogos

    def get_by_id(self, id: int) -> Optional[Catalogo]:
        """Get catalog item by ID"""
        return self.repository.get_by_id(id)

    def get_by_title(self, title: str) -> Optional[Catalogo]:
        """Get catalog item by title"""
        return self.repository.get_by_title(title)

    def inserir_catalogo(self, dados: Dict[str, Any]) -> bool:
        """
        RF 13 — act CatalogoService.inserirCatalogo / sd Cadastro Catalogo.

        Fluxo: verificar duplicidade por nome → criar Catalogo → criar
        MidiaFisica ou MidiaDigital → add_exemplar → persistir catálogo e exemplar.
        """
        titulo = str(dados.get("titulo", "")).strip()
        if not titulo:
            return False

        # 2: getCatalogoPorNome — se existir, retorna false (act)
        if self.repository.get_catalogo_por_nome(titulo):
            return False

        tipo_midia = str(dados.get("tipo_midia", "")).upper()
        if tipo_midia not in ("FISICA", "DIGITAL"):
            return False

        # 3: criar Catalogo
        catalogo = Catalogo(
            titulo=titulo,
            descricao=dados.get("descricao"),
            genero=dados.get("genero"),
            classificacao=dados.get("classificacao"),
            situacao=dados.get("situacao", StatusCatalogo.DISPONIVEL.value),
        )

        valor_venda = dados.get("valor_venda")
        valor_diaria = dados.get("valor_diaria_aluguel") or dados.get("valor_diaria")
        valor_venda_dec = (
            Decimal(str(valor_venda)) if valor_venda is not None else None
        )
        valor_diaria_dec = (
            Decimal(str(valor_diaria)) if valor_diaria is not None else None
        )

        # 4/5: criar MidiaFisica ou MidiaDigital
        if tipo_midia == "FISICA":
            codigo = str(dados.get("codigo_barras", "")).strip()
            estado = str(dados.get("estado_conservacao", "")).strip()
            if not codigo or not estado:
                return False
            exemplar = MidiaFisica(
                codigo_barras=codigo,
                catalogo=catalogo,
                estado_conservacao=estado,
                plataforma=dados.get("plataforma"),
                valor_venda=valor_venda_dec,
                valor_diaria_aluguel=valor_diaria_dec,
            )
        else:
            chave = str(dados.get("chave_ativacao", "")).strip()
            if not chave:
                return False
            data_expiracao = None
            if dados.get("data_expiracao"):
                data_expiracao = datetime.strptime(
                    dados["data_expiracao"], "%Y-%m-%d"
                ).date()
            exemplar = MidiaDigital(
                chave_ativacao=chave,
                catalogo=catalogo,
                data_expiracao=data_expiracao,
                plataforma=dados.get("plataforma"),
                valor_venda=valor_venda_dec,
                valor_diaria_aluguel=valor_diaria_dec,
            )

        # 6: add_exemplar na lista do catálogo (também feito no __init__ do Exemplar)
        catalogo.add_exemplar(exemplar)

        # 7 e 8: addCatalogo + addExemplar no repositório
        if not self.repository.add_catalogo(catalogo):
            return False
        return self.repository.add_exemplar(exemplar)

    def create(self, catalogo: Catalogo) -> Optional[Catalogo]:
        """Create a new catalog item with validation"""
        # Validate required fields
        if not catalogo.titulo:
            raise ValueError("Título é obrigatório")
        
        # Check for duplicates by title
        existing = self.repository.get_by_title(catalogo.titulo)
        if existing:
            raise ValueError(f"Jogo com título '{catalogo.titulo}' já existe")
        
        # Set default situacao if not provided
        if not catalogo.situacao:
            catalogo.situacao = StatusCatalogo.DISPONIVEL.value
        
        return self.repository.create(catalogo)

    def update(self, id: int, catalogo_data: dict) -> Optional[Catalogo]:
        """Update an existing catalog item"""
        catalogo = self.repository.get_by_id(id)
        if not catalogo:
            return None
        
        # Update fields
        if 'titulo' in catalogo_data:
            new_title = catalogo_data['titulo']
            # Check if title is being changed and if new title already exists
            if new_title != catalogo.titulo:
                existing = self.repository.get_by_title(new_title)
                if existing and existing.id != id:
                    raise ValueError(f"Jogo com título '{new_title}' já existe")
            catalogo.titulo = new_title
        
        if 'descricao' in catalogo_data:
            catalogo.descricao = catalogo_data['descricao']
        
        if 'genero' in catalogo_data:
            catalogo.genero = catalogo_data['genero']
        
        if 'classificacao' in catalogo_data:
            catalogo.classificacao = catalogo_data['classificacao']
        
        if 'situacao' in catalogo_data:
            catalogo.situacao = catalogo_data['situacao']
        
        return self.repository.update(catalogo)

    def delete(self, id: int) -> bool:
        """Delete a catalog item"""
        catalogo = self.repository.get_by_id(id)
        if not catalogo:
            return False
        
        return self.repository.delete(id)

    def get_by_genero(self, genero: str) -> List[Catalogo]:
        """Get catalog items by genre"""
        return self.repository.get_by_genero(genero)

    def get_by_situacao(self, situacao: str) -> List[Catalogo]:
        """Get catalog items by situation"""
        return self.repository.get_by_situacao(situacao)

    def inactivate(self, id: int) -> Optional[Catalogo]:
        """Inactivate a catalog item"""
        catalogo = self.repository.get_by_id(id)
        if not catalogo:
            return None
        
        catalogo.situacao = StatusCatalogo.INDISPONIVEL.value
        return self.repository.update(catalogo)

    def activate(self, id: int) -> Optional[Catalogo]:
        """Activate a catalog item"""
        catalogo = self.repository.get_by_id(id)
        if not catalogo:
            return None
        
        catalogo.situacao = StatusCatalogo.DISPONIVEL.value
        return self.repository.update(catalogo)
