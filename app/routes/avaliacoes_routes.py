import logging
from datetime import date
from flask import Blueprint, request, jsonify

from app.models import Cliente, Catalogo, Exemplar, Transacao, Venda, Aluguel, ItemTransacao, Avaliacao
from app.database.factories.database_manager import DatabaseManager

avaliacoes_bp = Blueprint('avaliacoes', __name__, url_prefix='/api/avaliacoes')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_cliente_from_header(session):
    cliente_id = request.headers.get('X-Cliente-Id')
    if not cliente_id:
        return None, "Header X-Cliente-Id é obrigatório."
    try:
        cliente_id = int(cliente_id)
    except ValueError:
        return None, "X-Cliente-Id inválido."

    cliente = session.query(Cliente).get(cliente_id)
    if not cliente:
        return None, "Cliente não cadastrado ou não encontrado."

    return cliente, None


def serialize_avaliacao(avaliacao: Avaliacao):
    return {
        "id": avaliacao.id,
        "id_transacao": avaliacao.id_transacao,
        "nota": avaliacao.nota,
        "comentario": avaliacao.comentario,
        "data_avaliacao": avaliacao.data_avaliacao.isoformat() if avaliacao.data_avaliacao else None
    }


_STATUS_FINALIZADO = {
    'venda': {'FINALIZADA'},
    'aluguel': {'FINALIZADO'}
}


@avaliacoes_bp.route('/<int:id_transacao>', methods=['POST'])
def avaliar_transacao(id_transacao):
    session = DatabaseManager.get_session()
    try:
        cliente, erro = get_cliente_from_header(session)
        if erro:
            return jsonify({"erro": erro}), 403

        data = request.get_json()
        if not data or 'nota' not in data:
            return jsonify({"erro": "O campo 'nota' é obrigatório."}), 400

        try:
            nota = int(data['nota'])
        except (TypeError, ValueError):
            return jsonify({"erro": "O campo 'nota' deve ser um número inteiro."}), 400

        if nota < 1 or nota > 5:
            return jsonify({"erro": "A nota deve ser um valor entre 1 e 5."}), 400

        comentario = data.get('comentario')

        transacao = session.query(Transacao).get(id_transacao)
        if not transacao or transacao.id_cliente != cliente.id_usuario:
            return jsonify({"erro": "Transação não encontrada ou não pertence a este cliente."}), 404

        status_esperado = _STATUS_FINALIZADO.get(transacao.tipo)
        if not status_esperado or transacao.status not in status_esperado:
            return jsonify({"erro": "Só é possível avaliar uma compra ou aluguel já finalizado."}), 400

        avaliacao_existente = session.query(Avaliacao).filter_by(id_transacao=id_transacao).first()
        if avaliacao_existente:
            return jsonify({"erro": "Esta transação já foi avaliada."}), 400

        nova_avaliacao = Avaliacao(
            id_transacao=id_transacao,
            nota=nota,
            comentario=comentario,
            data_avaliacao=date.today()
        )
        session.add(nova_avaliacao)
        session.commit()

        logger.info(f"Cliente ID {cliente.id_usuario} AVALIOU a transação ID {id_transacao} com nota {nota}.")
        return jsonify({
            "mensagem": "Avaliação registrada com sucesso.",
            "avaliacao": serialize_avaliacao(nova_avaliacao)
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        session.close()


@avaliacoes_bp.route('/minhas', methods=['GET'])
def minhas_avaliacoes():
    session = DatabaseManager.get_session()
    try:
        cliente, erro = get_cliente_from_header(session)
        if erro:
            return jsonify({"erro": erro}), 403

        avaliacoes = session.query(Avaliacao).join(
            Transacao, Transacao.id == Avaliacao.id_transacao
        ).filter(Transacao.id_cliente == cliente.id_usuario).all()

        return jsonify([serialize_avaliacao(a) for a in avaliacoes]), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()


@avaliacoes_bp.route('/jogo/<int:id_jogo>', methods=['GET'])
def avaliacoes_do_jogo(id_jogo):
    session = DatabaseManager.get_session()
    try:
        jogo = session.query(Catalogo).get(id_jogo)
        if not jogo:
            return jsonify({"erro": "Jogo não encontrado no catálogo."}), 404

        avaliacoes = session.query(Avaliacao).join(
            Transacao, Transacao.id == Avaliacao.id_transacao
        ).join(
            ItemTransacao, ItemTransacao.id_transacao == Transacao.id
        ).join(
            Exemplar, Exemplar.id == ItemTransacao.id_exemplar
        ).filter(Exemplar.id_catalogo == id_jogo).all()

        notas = [a.nota for a in avaliacoes if a.nota is not None]
        media = round(sum(notas) / len(notas), 2) if notas else None

        return jsonify({
            "id_jogo": id_jogo,
            "titulo": jogo.titulo,
            "media_nota": media,
            "total_avaliacoes": len(avaliacoes),
            "avaliacoes": [serialize_avaliacao(a) for a in avaliacoes]
        }), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()
