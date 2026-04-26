"""Rotas REST para o recurso Venda.

Refatorado para usar `Container` + `MockDataSource` em vez de SQLAlchemy.
Mantém o mesmo contrato HTTP, mas opera sobre os dados em memória.
"""

import logging
from datetime import datetime, date

from flask import request
from flask_restx import Namespace, Resource, fields

from app.container.container import container
from app.models import (
    Cliente,
    Catalogo,
    Exemplar,
    MidiaFisica,
    MidiaDigital,
    Aluguel,
    Venda,
    ItemTransacao,
)
from app.models.enums import StatusVenda, StatusCatalogo

vendas_ns = Namespace(
    'vendas',
    description='Operações relacionadas às vendas de jogos',
    path='/api/vendas',
)

venda_model = vendas_ns.model('Venda', {
    'id': fields.Integer(description='ID da venda'),
    'id_cliente': fields.Integer(description='ID do cliente'),
    'data_transacao': fields.Date(description='Data da transação'),
    'valor_total': fields.Float(description='Valor total'),
    'status': fields.String(description='Status da venda'),
})

venda_solicitacao_model = vendas_ns.model('VendaSolicitacao', {
    'id_jogo': fields.Integer(required=True, description='ID do jogo do catálogo'),
    'tipo_midia': fields.String(
        required=True, description='Tipo de mídia (FISICA ou DIGITAL)'
    ),
})

logger = logging.getLogger(__name__)


def _get_cliente_from_header():
    cliente_id = request.headers.get('X-Cliente-Id')
    if not cliente_id:
        return None, 'Header X-Cliente-Id é obrigatório.'
    try:
        cliente_id = int(cliente_id)
    except ValueError:
        return None, 'X-Cliente-Id inválido.'

    cliente = container.data_source.get_by_id(Cliente, cliente_id)
    if not cliente:
        return None, 'Cliente não cadastrado ou não encontrado.'
    return cliente, None


def _exemplares_indisponiveis() -> set:
    """Conjunto de IDs de exemplares ocupados por aluguéis ativos ou vendas finalizadas."""
    alugueis = container.data_source.get_all(Aluguel)
    vendas = container.data_source.get_all(Venda)
    itens = container.data_source.get_all(ItemTransacao)

    aluguel_ids = {
        a.id for a in alugueis
        if a.status in {'ATIVO', 'ATRASADO', 'SOLICITADO', 'APROVADO'}
    }
    venda_ids = {v.id for v in vendas if v.status == 'FINALIZADA'}

    indisponiveis = set()
    for item in itens:
        if item.id_transacao in aluguel_ids or item.id_transacao in venda_ids:
            indisponiveis.add(item.id_exemplar)
    return indisponiveis


def _find_exemplar_disponivel_venda(id_catalogo: int, tipo_midia: str):
    indisponiveis = _exemplares_indisponiveis()
    midias_fisicas = {m.id for m in container.data_source.get_all(MidiaFisica)}
    midias_digitais = {m.id for m in container.data_source.get_all(MidiaDigital)}

    for exemplar in container.data_source.get_all(Exemplar):
        if getattr(exemplar, 'id_catalogo', None) != id_catalogo:
            continue
        if exemplar.id in indisponiveis:
            continue
        situacao = getattr(exemplar, 'situacao', None)
        if situacao not in (None, 'DISPONIVEL'):
            continue
        if tipo_midia == 'FISICA' and exemplar.id in midias_fisicas:
            return exemplar
        if tipo_midia == 'DIGITAL' and exemplar.id in midias_digitais:
            return exemplar
    return None


def _serialize_venda(venda: Venda) -> dict:
    return {
        'id_transacao': venda.id,
        'data_transacao': (
            venda.data_transacao.isoformat() if venda.data_transacao else None
        ),
        'valor_total': float(venda.valor_total) if venda.valor_total else None,
        'status_venda': venda.status,
        'id_cliente': venda.id_cliente,
        'data_confirmacao': (
            venda.data_confirmacao.isoformat() if venda.data_confirmacao else None
        ),
    }


@vendas_ns.route('/solicitar')
class SolicitarVendaResource(Resource):
    @vendas_ns.expect(venda_solicitacao_model)
    def post(self):
        cliente, erro = _get_cliente_from_header()
        if erro:
            return {'erro': erro}, 403

        data = request.get_json() or {}
        for field in ('id_jogo', 'tipo_midia'):
            if not data.get(field):
                return {'erro': f"O campo '{field}' é obrigatório."}, 400

        jogo = container.data_source.get_by_id(Catalogo, int(data['id_jogo']))
        if not jogo or jogo.situacao != StatusCatalogo.DISPONIVEL.value:
            return {'erro': 'Jogo não existe ou está indisponível no catálogo.'}, 404

        tipo_midia = str(data['tipo_midia']).upper()
        if tipo_midia not in {'FISICA', 'DIGITAL'}:
            return {'erro': 'tipo_midia deve ser FISICA ou DIGITAL.'}, 400

        # Procura valor_venda no catálogo ou no exemplar específico
        exemplar = _find_exemplar_disponivel_venda(jogo.id, tipo_midia)
        if not exemplar:
            return {
                'erro': (
                    f'Não há exemplares da mídia {tipo_midia} disponíveis '
                    'no momento para este jogo.'
                )
            }, 400

        valor_total = (
            getattr(exemplar, 'valor_venda', None)
            or getattr(jogo, 'valor_venda', None)
        )
        if not valor_total:
            return {'erro': 'Valor de venda não definido para este jogo.'}, 400

        try:
            nova_venda = Venda(
                cliente=cliente,
                valor_total=valor_total,
                status=StatusVenda.FINALIZADA.value,
                data_transacao=datetime.utcnow(),
                data_confirmacao=date.today(),
            )
            criada = container.data_source.create(nova_venda)

            item = ItemTransacao(
                quantidade=1,
                valor_unitario=valor_total,
                transacao=criada,
            )
            item.exemplar = exemplar
            container.data_source.create(item)
            criada.adicionar_item(item)
        except Exception as exc:  # noqa: BLE001
            logger.exception('Erro ao criar venda')
            return {'erro': f'Erro interno: {exc}'}, 500

        logger.info(
            'Cliente ID %s COMPROU o jogo %r (Exemplar %s).',
            cliente.id, jogo.titulo, exemplar.id,
        )
        return {
            'mensagem': 'Venda realizada com sucesso.',
            'id_transacao': criada.id,
            'valor_total': float(valor_total),
        }, 201


@vendas_ns.route('/minhas-vendas')
class MinhasVendasResource(Resource):
    def get(self):
        cliente, erro = _get_cliente_from_header()
        if erro:
            return {'erro': erro}, 403

        try:
            vendas = [
                v for v in container.data_source.get_all(Venda)
                if v.id_cliente == cliente.id
            ]
            return [_serialize_venda(v) for v in vendas], 200
        except Exception as exc:  # noqa: BLE001
            logger.exception('Erro ao listar vendas')
            return {'erro': str(exc)}, 500


@vendas_ns.route('/<int:id>')
class DetalhesVendaResource(Resource):
    def get(self, id):
        cliente, erro = _get_cliente_from_header()
        if erro:
            return {'erro': erro}, 403

        venda = container.data_source.get_by_id(Venda, id)
        if not venda or venda.id_cliente != cliente.id:
            return {
                'erro': 'Venda não encontrada ou não pertence a este cliente.'
            }, 404
        return _serialize_venda(venda), 200


@vendas_ns.route('/<int:id>/cancelar')
class EstornarVendaResource(Resource):
    def patch(self, id):
        cliente, erro = _get_cliente_from_header()
        if erro:
            return {'erro': erro}, 403

        venda = container.data_source.get_by_id(Venda, id)
        if not venda or venda.id_cliente != cliente.id:
            return {
                'erro': 'Venda não encontrada ou não pertence a este cliente.'
            }, 404

        if venda.status == 'ESTORNADA':
            return {'erro': 'Esta venda já foi estornada.'}, 400

        venda.status = 'ESTORNADA'
        container.data_source.update(venda)
        logger.info(
            'Cliente ID %s SOLICITOU ESTORNO da venda ID %s.',
            cliente.id, venda.id,
        )
        return {'mensagem': 'Venda estornada com sucesso.'}, 200
