from app.models.catalogo.catalogo import Catalogo
from app.models.enums import StatusCatalogo


class CatalogoDTO:
    @staticmethod
    def from_model(catalogo: Catalogo) -> dict:
        """
        Converte um objeto Catalogo em um dicionário DTO,
        gerando o resumo consolidado de exemplares disponíveis,
        plataformas e tipos de mídia atrelados a este catalogo.
        """
        # Evita erro caso 'exemplares' não esteja preenchido
        exemplares = catalogo.exemplares if catalogo.exemplares else []

        quantidade_disponivel = sum(1 for ex in exemplares if ex.situacao == StatusCatalogo.DISPONIVEL.value)

        # Utiliza `set` para garantir itens únicos, descartando valores nulos
        plataformas = list({ex.plataforma for ex in exemplares if getattr(ex, 'plataforma', None)})
        tipos_midia = list({ex.tipo_midia for ex in exemplares if getattr(ex, 'tipo_midia', None)})

        return {
            "id": catalogo.id,
            "titulo": catalogo.titulo,
            "descricao": catalogo.descricao,
            "ativo": catalogo.ativo,
            "genero": catalogo.genero,
            "classificacao": catalogo.classificacao,
            "quantidade_disponivel": quantidade_disponivel,
            "plataformas_disponiveis": plataformas,
            "tipos_midia_disponiveis": tipos_midia
        }