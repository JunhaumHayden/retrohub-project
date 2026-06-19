import logging
from datetime import datetime
from flask import Blueprint, request, jsonify

from app.models import Funcionario, Catalogo, Exemplar, Venda, Aluguel, ItemTransacao
from app.database.factories.database_manager import DatabaseManager

relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/api/relatorios')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_funcionario_from_header(session):
    func_id = request.headers.get('X-Funcionario-Id')
    if not func_id:
        func_id = request.headers.get('X-Admin-Id')
    if not func_id:
        return None, "Header X-Funcionario-Id (ou X-Admin-Id) é obrigatório para esta operação."
    try:
        func_id = int(func_id)
    except ValueError:
        return None, "O ID do funcionário deve ser um número inteiro."
    funcionario = session.get(Funcionario, func_id)
    if not funcionario:
        return None, "Funcionário não encontrado."
    return funcionario, None


def parse_data(valor, nome_campo):
    if not valor:
        return None, None
    try:
        return datetime.strptime(valor, '%Y-%m-%d').date(), None
    except ValueError:
        return None, f"Formato de '{nome_campo}' inválido. Use AAAA-MM-DD."


@relatorios_bp.route('/compras-locacoes', methods=['GET'])
def relatorio_compras_locacoes():
    session = DatabaseManager.get_session()
    try:
        _, erro = get_funcionario_from_header(session)
        if erro:
            return jsonify({"erro": erro}), 403

        data_inicio, erro = parse_data(request.args.get('data_inicio'), 'data_inicio')
        if erro:
            return jsonify({"erro": erro}), 400
        data_fim, erro = parse_data(request.args.get('data_fim'), 'data_fim')
        if erro:
            return jsonify({"erro": erro}), 400

        vendas_query = session.query(Venda).filter(Venda.status == 'FINALIZADA')
        alugueis_query = session.query(Aluguel).filter(Aluguel.status.in_(['ATIVO', 'FINALIZADO', 'ATRASADO']))

        if data_inicio:
            vendas_query = vendas_query.filter(Venda.data_transacao >= data_inicio)
            alugueis_query = alugueis_query.filter(Aluguel.data_transacao >= data_inicio)
        if data_fim:
            vendas_query = vendas_query.filter(Venda.data_transacao <= data_fim)
            alugueis_query = alugueis_query.filter(Aluguel.data_transacao <= data_fim)

        vendas = vendas_query.all()
        alugueis = alugueis_query.all()

        total_vendas = len(vendas)
        total_alugueis = len(alugueis)
        receita_vendas = sum(float(v.valor_total) for v in vendas if v.valor_total)
        receita_alugueis = sum(float(a.valor_total) for a in alugueis if a.valor_total)

        por_jogo = {}

        def registrar(transacao_id, valor, campo_quantidade, campo_receita):
            item = session.query(ItemTransacao).filter_by(id_transacao=transacao_id).first()
            if not item:
                return
            exemplar = session.get(Exemplar, item.id_exemplar)
            if not exemplar:
                return
            jogo = session.get(Catalogo, exemplar.id_catalogo)
            if not jogo:
                return
            registro = por_jogo.setdefault(jogo.id, {
                "id_catalogo": jogo.id,
                "titulo": jogo.titulo,
                "quantidade_vendida": 0,
                "receita_vendas": 0.0,
                "quantidade_alugada": 0,
                "receita_alugueis": 0.0
            })
            registro[campo_quantidade] += 1
            registro[campo_receita] += float(valor) if valor else 0.0

        for v in vendas:
            registrar(v.id, v.valor_total, "quantidade_vendida", "receita_vendas")
        for a in alugueis:
            registrar(a.id, a.valor_total, "quantidade_alugada", "receita_alugueis")

        return jsonify({
            "periodo": {
                "data_inicio": data_inicio.isoformat() if data_inicio else None,
                "data_fim": data_fim.isoformat() if data_fim else None
            },
            "resumo": {
                "total_vendas": total_vendas,
                "receita_total_vendas": round(receita_vendas, 2),
                "total_alugueis": total_alugueis,
                "receita_total_alugueis": round(receita_alugueis, 2),
                "receita_total": round(receita_vendas + receita_alugueis, 2)
            },
            "por_jogo": sorted(por_jogo.values(), key=lambda r: r["titulo"])
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        session.close()
