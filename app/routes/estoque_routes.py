"""Rotas REST para o recurso Estoque (Exemplares físicos e digitais).

Refatorado para utilizar o `Container` + `MockDataSource`. As operações de
estoque continuam exigindo identificação do funcionário via `X-Funcionario-Id`
ou `X-Admin-Id`.
"""

import logging
from datetime import datetime

from flask import request
from flask_restx import Namespace, Resource, fields

from app.container.container import container
from app.models import (
    Catalogo,
    Exemplar,
    MidiaFisica,
    MidiaDigital,
    Funcionario,
)

estoque_ns = Namespace(
    'estoque',
    description='Operações relacionadas ao estoque de jogos',
    path='/api/estoque',
)

midia_fisica_model = estoque_ns.model('MidiaFisica', {
    'id': fields.Integer(description='ID do exemplar'),
    'id_catalogo': fields.Integer(description='ID do catálogo'),
    'tipo_midia': fields.String(description='Tipo de mídia'),
    'codigo_barras': fields.String(description='Código de barras'),
    'estado_conservacao': fields.String(description='Estado de conservação'),
})

midia_digital_model = estoque_ns.model('MidiaDigital', {
    'id': fields.Integer(description='ID do exemplar'),
    'id_catalogo': fields.Integer(description='ID do catálogo'),
    'tipo_midia': fields.String(description='Tipo de mídia'),
    'chave_ativacao': fields.String(description='Chave de ativação'),
})

midia_fisica_input_model = estoque_ns.model('MidiaFisicaInput', {
    'id_catalogo': fields.Integer(required=True, description='ID do catálogo'),
    'codigo_barras': fields.String(required=True, description='Código de barras'),
    'estado_conservacao': fields.String(description='Estado de conservação'),
})

midia_digital_input_model = estoque_ns.model('MidiaDigitalInput', {
    'id_catalogo': fields.Integer(required=True, description='ID do catálogo'),
    'chave_ativacao': fields.String(required=True, description='Chave de ativação'),
})

logger = logging.getLogger(__name__)


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

    funcionario = container.data_source.get_by_id(Funcionario, func_id)
    if not funcionario:
        return None, 'Funcionário não encontrado.'
    return funcionario, None


def _serialize_exemplar(exemplar: Exemplar) -> dict:
    base = {
        'id': exemplar.id,
        'id_catalogo': getattr(exemplar, 'id_catalogo', None),
        'tipo_midia': exemplar.tipo_midia,
        'situacao': getattr(exemplar, 'situacao', None),
    }
    if isinstance(exemplar, MidiaFisica):
        base.update({
            'codigo_barras': exemplar.codigo_barras,
            'estado_conservacao': exemplar.estado_conservacao,
            'plataforma': getattr(exemplar, 'plataforma', None),
            'valor_venda': (
                float(exemplar.valor_venda) if exemplar.valor_venda else None
            ),
            'valor_diaria_aluguel': (
                float(exemplar.valor_diaria_aluguel)
                if exemplar.valor_diaria_aluguel else None
            ),
        })
    elif isinstance(exemplar, MidiaDigital):
        base.update({
            'chave_ativacao': exemplar.chave_ativacao,
            'data_expiracao': (
                exemplar.data_expiracao.isoformat()
                if exemplar.data_expiracao else None
            ),
            'plataforma': getattr(exemplar, 'plataforma', None),
            'valor_venda': (
                float(exemplar.valor_venda) if exemplar.valor_venda else None
            ),
            'valor_diaria_aluguel': (
                float(exemplar.valor_diaria_aluguel)
                if exemplar.valor_diaria_aluguel else None
            ),
        })
    return base


@estoque_ns.route('/fisico')
class MidiaFisicaResource(Resource):
    @estoque_ns.expect(midia_fisica_input_model)
    def post(self):
        funcionario, erro = _get_funcionario_from_header()
        if erro:
            return {'erro': erro}, 403

        data = request.get_json() or {}
        for field in ('id_catalogo', 'codigo_barras', 'estado_conservacao'):
            if not str(data.get(field, '')).strip():
                return {'erro': f"O campo '{field}' é obrigatório."}, 400

        catalogo = container.data_source.get_by_id(
            Catalogo, int(data['id_catalogo'])
        )
        if not catalogo:
            return {'erro': 'Jogo não encontrado no catálogo.'}, 404

        existentes = container.data_source.get_all(MidiaFisica)
        if any(m.codigo_barras == data['codigo_barras'] for m in existentes):
            return {
                'erro': (
                    f"O código de barras '{data['codigo_barras']}' já está "
                    'cadastrado no sistema.'
                )
            }, 400

        nova = MidiaFisica(
            codigo_barras=data['codigo_barras'],
            catalogo=catalogo,
            estado_conservacao=data['estado_conservacao'],
        )
        criada = container.data_source.create(nova)
        logger.info(
            "Funcionário ID %s cadastrou mídia FÍSICA '%s' para o jogo '%s'.",
            funcionario.id, criada.codigo_barras, catalogo.titulo,
        )
        return _serialize_exemplar(criada), 201


@estoque_ns.route('/digital')
class MidiaDigitalResource(Resource):
    @estoque_ns.expect(midia_digital_input_model)
    def post(self):
        funcionario, erro = _get_funcionario_from_header()
        if erro:
            return {'erro': erro}, 403

        data = request.get_json() or {}
        for field in ('id_catalogo', 'chave_ativacao'):
            if not str(data.get(field, '')).strip():
                return {'erro': f"O campo '{field}' é obrigatório."}, 400

        catalogo = container.data_source.get_by_id(
            Catalogo, int(data['id_catalogo'])
        )
        if not catalogo:
            return {'erro': 'Jogo não encontrado no catálogo.'}, 404

        existentes = container.data_source.get_all(MidiaDigital)
        if any(m.chave_ativacao == data['chave_ativacao'] for m in existentes):
            return {
                'erro': 'Esta chave de ativação já está cadastrada no sistema.'
            }, 400

        data_expiracao = None
        if data.get('data_expiracao'):
            try:
                data_expiracao = datetime.strptime(
                    data['data_expiracao'], '%Y-%m-%d'
                ).date()
            except ValueError:
                return {'erro': 'Formato de data inválido. Use AAAA-MM-DD.'}, 400

        nova = MidiaDigital(
            chave_ativacao=data['chave_ativacao'],
            catalogo=catalogo,
            data_expiracao=data_expiracao,
        )
        criada = container.data_source.create(nova)
        logger.info(
            "Funcionário ID %s cadastrou mídia DIGITAL para o catálogo '%s'.",
            funcionario.id, catalogo.titulo,
        )
        return _serialize_exemplar(criada), 201


@estoque_ns.route('/catalogo/<int:id_catalogo>')
class EstoqueCatalogoResource(Resource):
    def get(self, id_catalogo):
        catalogo = container.data_source.get_by_id(Catalogo, id_catalogo)
        if not catalogo:
            return {'erro': 'Jogo não encontrado no catálogo.'}, 404

        exemplares = [
            ex for ex in container.data_source.get_all(Exemplar)
            if getattr(ex, 'id_catalogo', None) == id_catalogo
        ]
        return [_serialize_exemplar(ex) for ex in exemplares], 200


@estoque_ns.route('/fisico/<int:id>')
class MidiaFisicaEstadoResource(Resource):
    def put(self, id):
        funcionario, erro = _get_funcionario_from_header()
        if erro:
            return {'erro': erro}, 403

        data = request.get_json() or {}
        if not data.get('estado_conservacao'):
            return {
                'erro': "O campo 'estado_conservacao' é obrigatório."
            }, 400

        midia = container.data_source.get_by_id(MidiaFisica, id)
        if not midia:
            return {'erro': 'Exemplar físico não encontrado.'}, 404

        estado_antigo = midia.estado_conservacao
        midia.estado_conservacao = data['estado_conservacao']
        container.data_source.update(midia)
        logger.info(
            "Funcionário ID %s ATUALIZOU o estado da mídia %s de '%s' para '%s'.",
            funcionario.id, midia.codigo_barras,
            estado_antigo, midia.estado_conservacao,
        )
        return _serialize_exemplar(midia), 200


@estoque_ns.route('/<int:id>')
class ExemplarResource(Resource):
    def delete(self, id):
        funcionario, erro = _get_funcionario_from_header()
        if erro:
            return {'erro': erro}, 403

        exemplar = container.data_source.get_by_id(Exemplar, id)
        if not exemplar:
            return {'erro': 'Exemplar não encontrado.'}, 404

        tipo = exemplar.tipo_midia
        removido = container.data_source.delete(type(exemplar), id)
        if not removido:
            return {'erro': 'Exemplar não encontrado.'}, 404
        logger.warning(
            'Funcionário ID %s EXCLUIU o exemplar ID %s (%s).',
            funcionario.id, id, tipo,
        )
        return {'mensagem': 'Exemplar excluído do estoque com sucesso.'}, 200
