import logging
from datetime import datetime, date
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import not_, or_

from app.models import Cliente, Catalogo, Exemplar, MidiaFisica, MidiaDigital, Transacao, Aluguel, Venda, ItemTransacao
from app.database.factories.database_manager import DatabaseManager

vendas_bp = Blueprint('vendas', __name__, url_prefix='/api/vendas')

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

def find_exemplar_disponivel_venda(session, id_jogo, tipo_midia):
    if tipo_midia == 'DIGITAL':
        alugueis_ocupando_ids = session.query(Aluguel.id_transacao).filter(
            Aluguel.status.in_(['ATIVO', 'ATRASADO', 'SOLICITADO', 'APROVADO'])
        )
        vendas_ids = session.query(Venda.id_transacao).filter(Venda.status == 'FINALIZADA')
        exemplares_indisponiveis = session.query(ItemTransacao.id_exemplar).filter(
            or_(
                ItemTransacao.id_transacao.in_(alugueis_ocupando_ids),
                ItemTransacao.id_transacao.in_(vendas_ids)
            )
        )
        return session.query(Exemplar).join(MidiaDigital).filter(
            Exemplar.id_jogo == id_jogo,
            or_(Exemplar.situacao.is_(None), Exemplar.situacao == 'DISPONIVEL'),
            not_(Exemplar.id.in_(exemplares_indisponiveis))
        ).first()
        
    elif tipo_midia == 'FISICA':
        # Físico: precisa buscar um exemplar que não esteja em um Aluguel ATIVO/ATRASADO nem em uma Venda FINALIZADA
        
        alugueis_ativos_ids = session.query(Aluguel.id_transacao).filter(
            Aluguel.status.in_(['ATIVO', 'ATRASADO', 'SOLICITADO', 'APROVADO'])
        )
        vendas_ids = session.query(Venda.id_transacao).filter(Venda.status == 'FINALIZADA')

        exemplares_indisponiveis = session.query(ItemTransacao.id_exemplar).filter(
            or_(
                ItemTransacao.id_transacao.in_(alugueis_ativos_ids),
                ItemTransacao.id_transacao.in_(vendas_ids)
            )
        )

        exemplar = session.query(Exemplar).join(MidiaFisica).filter(
            Exemplar.id_jogo == id_jogo,
            or_(Exemplar.situacao.is_(None), Exemplar.situacao == 'DISPONIVEL'),
            not_(Exemplar.id.in_(exemplares_indisponiveis))
        ).first()
        
        return exemplar
    return None

def serialize_venda(venda: Venda):
    return {
        "id_transacao": venda.id,
        "data_transacao": venda.data_transacao.isoformat() if venda.data_transacao else None,
        "valor_total": float(venda.valor_total) if venda.valor_total else None,
        "status_venda": venda.status,
        "id_cliente": venda.id_cliente,
        "data_confirmacao": venda.data_confirmacao.isoformat() if venda.data_confirmacao else None
    }


@vendas_bp.route('/solicitar', methods=['POST'])
def solicitar_venda():
    session = DatabaseManager.get_session()
    try:
        cliente, erro = get_cliente_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        data = request.get_json()
        if not data: return jsonify({"erro": "Dados não fornecidos."}), 400

        required_fields = ['id_jogo', 'tipo_midia']
        for field in required_fields:
            if field not in data or str(data[field]).strip() == "":
                return jsonify({"erro": f"O campo '{field}' é obrigatório."}), 400

        jogo = session.query(Catalogo).get(data['id_jogo'])
        if not jogo or not jogo.ativo:
            return jsonify({"erro": "Jogo não existe ou está inativo no catálogo."}), 404

        if not jogo.valor_venda:
            return jsonify({"erro": "Este jogo não está disponível para venda (valor de venda não definido)."}), 400

        tipo_midia = str(data['tipo_midia']).upper()
        if tipo_midia not in ['FISICA', 'DIGITAL']:
            return jsonify({"erro": "tipo_midia deve ser FISICA ou DIGITAL."}), 400

        # Buscar exemplar disponível (Dar baixa no estoque)
        exemplar_disponivel = find_exemplar_disponivel_venda(session, jogo.id, tipo_midia)
        if not exemplar_disponivel:
            return jsonify({"erro": f"Não há exemplares da mídia {tipo_midia} disponíveis no momento para este jogo."}), 400

        valor_total = jogo.valor_venda

        nova_venda = Venda(
            id_cliente=cliente.id_usuario,
            valor_total=valor_total,
            status='FINALIZADA', # Em um sistema real seria PENDENTE aguardando pagamento
            data_transacao=datetime.utcnow(),
            data_confirmacao=date.today()
        )
        
        session.add(nova_venda)
        session.flush() # Gerar o ID da venda

        # Criar Item da Transação vinculando ao Exemplar
        item = ItemTransacao(
            id_transacao=nova_venda.id,
            id_exemplar=exemplar_disponivel.id,
            valor_unitario=valor_total
        )
        
        session.add(item)
        session.commit()

        logger.info(f"Cliente ID {cliente.id_usuario} COMPROU o jogo '{jogo.titulo}' (Exemplar {exemplar_disponivel.id}).")
        return jsonify({
            "mensagem": "Venda realizada com sucesso.",
            "id_transacao": nova_venda.id,
            "valor_total": float(valor_total)
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        session.close()

@vendas_bp.route('/minhas-vendas', methods=['GET'])
def minhas_vendas():
    session = DatabaseManager.get_session()
    try:
        cliente, erro = get_cliente_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        vendas = session.query(Venda).filter_by(id_cliente=cliente.id_usuario).all()
        return jsonify([serialize_venda(v) for v in vendas]), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()

@vendas_bp.route('/<int:id>', methods=['GET'])
def detalhes_venda(id):
    session = DatabaseManager.get_session()
    try:
        cliente, erro = get_cliente_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        venda = session.query(Venda).get(id)
        if not venda or venda.id_cliente != cliente.id_usuario:
            return jsonify({"erro": "Venda não encontrada ou não pertence a este cliente."}), 404

        return jsonify(serialize_venda(venda)), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()

@vendas_bp.route('/<int:id>/cancelar', methods=['PATCH'])
def estornar_venda(id):
    session = DatabaseManager.get_session()
    try:
        cliente, erro = get_cliente_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        venda = session.query(Venda).get(id)
        if not venda or venda.id_cliente != cliente.id_usuario:
            return jsonify({"erro": "Venda não encontrada ou não pertence a este cliente."}), 404

        if venda.status == 'ESTORNADA':
            return jsonify({"erro": "Esta venda já foi estornada."}), 400

        venda.status = 'ESTORNADA'
        
        session.commit()
        logger.info(f"Cliente ID {cliente.id_usuario} SOLICITOU ESTORNO da venda ID {venda.id}.")
        return jsonify({"mensagem": "Venda estornada com sucesso."}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()
