"""Rotas REST para o recurso Catalogo (itens de jogos).

Refatoradas para o padrão: uma `Resource` por rota, com todos os verbos
(GET/POST/PUT/DELETE) agrupados. Isso deixa a documentação Swagger
limpa e organizada em ``/api/catalogo/itens/`` e
``/api/catalogo/itens/<id>``.
"""

import logging

from flask import request
from flask_restx import Namespace, Resource, fields

from app.container.container import container
from app.models import Catalogo
from app.models.enums import StatusCatalogo

catalogo_ns = Namespace(
    'catalogo',
    description='Operações relacionadas ao catálogo de jogos',
    path='/api/catalogo/itens',
)

catalogo_model = catalogo_ns.model('Catalogo', {
    'id': fields.Integer(description='ID do jogo'),
    'titulo': fields.String(description='Título do jogo'),
    'descricao': fields.String(description='Descrição do jogo'),
    'situacao': fields.String(description='Situação do jogo'),
    'genero': fields.String(description='Gênero do jogo'),
    'classificacao': fields.String(description='Classificação do jogo'),
    'estoque_disponivel': fields.Integer(
        description='Quantidade de exemplares disponíveis',
    ),
})

catalogo_input_model = catalogo_ns.model('CatalogoInput', {
    'titulo': fields.String(required=True, description='Título do jogo'),
    'descricao': fields.String(description='Descrição do jogo'),
    'genero': fields.String(description='Gênero do jogo'),
    'classificacao': fields.String(description='Classificação do jogo'),
    'situacao': fields.String(
        description='Situação do jogo',
        default=StatusCatalogo.DISPONIVEL.value,
    ),
})

logger = logging.getLogger(__name__)


def _serialize_catalogo(jogo: Catalogo) -> dict:
    return {
        'id': jogo.id,
        'titulo': jogo.titulo,
        'descricao': jogo.descricao,
        'situacao': jogo.situacao,
        'genero': jogo.genero,
        'classificacao': jogo.classificacao,
        'estoque_disponivel': getattr(jogo, 'estoque_disponivel', 0),
    }


def _get_funcionario_from_header():
    func_id = request.headers.get('X-Funcionario-Id') or request.headers.get(
        'X-Admin-Id'
    )
    if not func_id:
        return None, (
            'Header X-Funcionario-Id (ou X-Admin-Id) é obrigatório para '
            'esta operação.'
        )
    try:
        func_id = int(func_id)
    except ValueError:
        return None, 'O ID do funcionário deve ser um número inteiro.'

    funcionario = container.usuario_service.get_funcionario_by_id(func_id)
    if not funcionario:
        return None, 'Funcionário não encontrado.'
    return funcionario, None


@catalogo_ns.route('/')
class CatalogoListResource(Resource):
    @catalogo_ns.doc(
        params={
            'situacao': "Filtra por situação (ex: 'DISPONIVEL').",
        }
    )
    def get(self):
        """Lista todos os itens do catálogo (com filtro opcional)."""
        try:
            situacao_param = request.args.get('situacao')
            catalogos = container.catalogo_service.list_all(situacao_param)
            return [_serialize_catalogo(j) for j in catalogos], 200
        except Exception as e:  # pragma: no cover - defensive
            logger.error('Erro em listar_catalogos: %s', e)
            return {'erro': 'Erro ao buscar catálogo.'}, 500

    @catalogo_ns.expect(catalogo_input_model)
    def post(self):
        """Cria um novo item no catálogo (requer funcionário)."""
        funcionario, erro = _get_funcionario_from_header()
        if erro:
            return {'erro': erro}, 403

        data = request.get_json() or {}
        if not str(data.get('titulo', '')).strip():
            return {'erro': "O campo 'titulo' é obrigatório."}, 400

        novo_catalogo = Catalogo(
            id=None,
            titulo=data['titulo'],
            descricao=data.get('descricao'),
            genero=data.get('genero'),
            classificacao=data.get('classificacao'),
            situacao=data.get('situacao', StatusCatalogo.DISPONIVEL.value),
        )

        try:
            criado = container.catalogo_service.create(novo_catalogo)
        except ValueError as e:
            return {'erro': str(e)}, 400

        logger.info(
            "Funcionário ID %s criou novo item no catálogo: '%s'",
            funcionario.id, criado.titulo,
        )
        return {
            'mensagem': 'Item criado com sucesso!',
            'item': _serialize_catalogo(criado),
        }, 201


@catalogo_ns.route('/<int:id>')
@catalogo_ns.param('id', 'ID do item do catálogo')
class CatalogoDetailResource(Resource):
    def get(self, id):
        """Retorna o detalhe de um item do catálogo."""
        jogo = container.catalogo_service.get_by_id(id)
        if not jogo:
            return {'erro': 'Catalogo não encontrado.'}, 404
        return _serialize_catalogo(jogo), 200

    @catalogo_ns.expect(catalogo_input_model)
    def put(self, id):
        """Atualiza um item do catálogo (requer funcionário)."""
        funcionario, erro = _get_funcionario_from_header()
        if erro:
            return {'erro': erro}, 403

        data = request.get_json() or {}
        if not data:
            return {'erro': 'Dados não fornecidos.'}, 400

        try:
            atualizado = container.catalogo_service.update(id, data)
        except ValueError as e:
            return {'erro': str(e)}, 400

        if not atualizado:
            return {'erro': 'Catalogo não encontrado.'}, 404

        logger.info(
            'Funcionário ID %s atualizou o jogo ID %s', funcionario.id, id,
        )
        return {
            'mensagem': 'Item atualizado com sucesso!',
            'item': _serialize_catalogo(atualizado),
        }, 200

    def delete(self, id):
        """Inativa (soft delete) um item do catálogo."""
        funcionario, erro = _get_funcionario_from_header()
        if erro:
            return {'erro': erro}, 403

        inativado = container.catalogo_service.inactivate(id)
        if not inativado:
            return {'erro': 'Catalogo não encontrado.'}, 404

        logger.info(
            'Funcionário ID %s inativou o jogo ID %s', funcionario.id, id,
        )
        return {
            'mensagem': 'Item inativado com sucesso.',
            'item': _serialize_catalogo(inativado),
        }, 200
