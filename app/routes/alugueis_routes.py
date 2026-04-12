import logging
from datetime import datetime, timedelta, date
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_, not_

from app.models import Cliente, Jogo, Exemplar, MidiaFisica, MidiaDigital, Transacao, Aluguel, Venda, ItemTransacao
from app.database.factories.database_manager import DatabaseManager

alugueis_bp = Blueprint('alugueis', __name__, url_prefix='/api/alugueis')

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

def find_exemplar_disponivel(session, id_jogo, tipo_midia):
    if tipo_midia == 'DIGITAL':
        # Digital é infinito, basta ter um cadastrado
        return session.query(Exemplar).join(MidiaDigital).filter(Exemplar.id_jogo == id_jogo).first()
        
    elif tipo_midia == 'FISICA':
        # Físico: precisa buscar um exemplar que não esteja em um Aluguel ATIVO/ATRASADO nem em uma Venda FINALIZADA
        
        alugueis_ativos_ids = session.query(Aluguel.id_transacao).filter(Aluguel.status.in_(['ATIVO', 'ATRASADO']))
        vendas_ids = session.query(Venda.id_transacao).filter(Venda.status == 'FINALIZADA')

        exemplares_indisponiveis = session.query(ItemTransacao.id_exemplar).filter(
            or_(
                ItemTransacao.id_transacao.in_(alugueis_ativos_ids),
                ItemTransacao.id_transacao.in_(vendas_ids)
            )
        )

        exemplar = session.query(Exemplar).join(MidiaFisica).filter(
            Exemplar.id_jogo == id_jogo,
            not_(Exemplar.id.in_(exemplares_indisponiveis))
        ).first()
        
        return exemplar
    return None

def serialize_aluguel(aluguel: Aluguel):
    return {
        "id_transacao": aluguel.id,
        "data_transacao": aluguel.data_transacao.isoformat() if aluguel.data_transacao else None,
        "valor_total": float(aluguel.valor_total) if aluguel.valor_total else None,
        "status_transacao": aluguel.status,
        "id_cliente": aluguel.id_cliente,
        "periodo_dias": aluguel.periodo,
        "data_inicio": aluguel.data_inicio.isoformat() if aluguel.data_inicio else None,
        "data_prevista_devolucao": aluguel.data_prevista_devolucao.isoformat() if aluguel.data_prevista_devolucao else None,
        "data_devolucao": aluguel.data_devolucao.isoformat() if aluguel.data_devolucao else None,
        "status_aluguel": getattr(aluguel, 'status', 'ATIVO') 
    }


@alugueis_bp.route('/solicitar', methods=['POST'])
def solicitar_aluguel():
    session = DatabaseManager.get_session()
    try:
        cliente, erro = get_cliente_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        data = request.get_json()
        if not data: return jsonify({"erro": "Dados não fornecidos."}), 400

        required_fields = ['id_jogo', 'dias_alugados', 'data_inicio', 'tipo_midia']
        for field in required_fields:
            if field not in data or str(data[field]).strip() == "":
                return jsonify({"erro": f"O campo '{field}' é obrigatório."}), 400

        dias_alugados = int(data['dias_alugados'])
        if dias_alugados <= 0 or dias_alugados > 30:
            return jsonify({"erro": "O período de aluguel deve ser entre 1 e 30 dias."}), 400

        try:
            data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"erro": "Formato de data_inicio inválido. Use AAAA-MM-DD."}), 400

        if data_inicio < date.today():
            return jsonify({"erro": "A data de início não pode ser anterior à data atual."}), 400

        jogo = session.query(Jogo).get(data['id_jogo'])
        if not jogo or not jogo.ativo:
            return jsonify({"erro": "Jogo não existe ou está inativo no catálogo."}), 404

        if not jogo.valor_diaria_aluguel:
            return jsonify({"erro": "Este jogo não está disponível para aluguel (valor da diária não definido)."}), 400

        tipo_midia = str(data['tipo_midia']).upper()
        if tipo_midia not in ['FISICA', 'DIGITAL']:
            return jsonify({"erro": "tipo_midia deve ser FISICA ou DIGITAL."}), 400

        # Buscar exemplar disponível (Dar baixa no estoque temporariamente)
        exemplar_disponivel = find_exemplar_disponivel(session, jogo.id, tipo_midia)
        if not exemplar_disponivel:
            return jsonify({"erro": f"Não há exemplares da mídia {tipo_midia} disponíveis no momento para este jogo."}), 400

        # Calcular valor total
        valor_total = jogo.valor_diaria_aluguel * dias_alugados
        data_prevista_devolucao = data_inicio + timedelta(days=dias_alugados)

        novo_aluguel = Aluguel(
            id_cliente=cliente.id_usuario,
            valor_total=valor_total,
            status='PENDENTE', # Transação fica PENDENTE de pagamento/aprovação
            data_transacao=datetime.utcnow(),
            periodo=dias_alugados,
            data_inicio=data_inicio,
            data_prevista_devolucao=data_prevista_devolucao
        )
        
        novo_aluguel.status = 'ATIVO'

        session.add(novo_aluguel)
        session.flush() # Gerar o ID do aluguel

        # Criar Item da Transação vinculando ao Exemplar
        item = ItemTransacao(
            id_transacao=novo_aluguel.id,
            id_exemplar=exemplar_disponivel.id,
            valor_unitario=valor_total
        )
        session.add(item)
        session.commit()

        logger.info(f"Cliente ID {cliente.id_usuario} solicitou ALUGUEL do jogo '{jogo.titulo}' (Exemplar {exemplar_disponivel.id}) por {dias_alugados} dias.")
        return jsonify({
            "mensagem": "Aluguel solicitado com sucesso.",
            "id_transacao": novo_aluguel.id,
            "valor_total": float(valor_total),
            "data_prevista_devolucao": data_prevista_devolucao.isoformat()
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        session.close()

@alugueis_bp.route('/meus-alugueis', methods=['GET'])
def meus_alugueis():
    session = DatabaseManager.get_session()
    try:
        cliente, erro = get_cliente_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        alugueis = session.query(Aluguel).filter_by(id_cliente=cliente.id_usuario).all()
        return jsonify([serialize_aluguel(a) for a in alugueis]), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()

@alugueis_bp.route('/<int:id>', methods=['GET'])
def detalhes_aluguel(id):
    session = DatabaseManager.get_session()
    try:
        cliente, erro = get_cliente_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        aluguel = session.query(Aluguel).get(id)
        if not aluguel or aluguel.id_cliente != cliente.id_usuario:
            return jsonify({"erro": "Aluguel não encontrado ou não pertence a este cliente."}), 404

        return jsonify(serialize_aluguel(aluguel)), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()

@alugueis_bp.route('/<int:id>/cancelar', methods=['PATCH'])
def cancelar_aluguel(id):
    session = DatabaseManager.get_session()
    try:
        cliente, erro = get_cliente_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        aluguel = session.query(Aluguel).get(id)
        if not aluguel or aluguel.id_cliente != cliente.id_usuario:
            return jsonify({"erro": "Aluguel não encontrado ou não pertence a este cliente."}), 404

        if aluguel.data_inicio <= date.today():
            return jsonify({"erro": "Não é possível cancelar um aluguel que já iniciou ou está no dia de retirada."}), 400

        aluguel.status = 'FINALIZADO' # Status do Aluguel
        
        session.commit()
        logger.info(f"Cliente ID {cliente.id_usuario} CANCELOU o aluguel ID {aluguel.id}.")
        return jsonify({"mensagem": "Aluguel cancelado com sucesso."}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()

@alugueis_bp.route('/<int:id>/renovar', methods=['PATCH'])
def renovar_aluguel(id):
    session = DatabaseManager.get_session()
    try:
        cliente, erro = get_cliente_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        data = request.get_json()
        if not data or 'dias_adicionais' not in data:
            return jsonify({"erro": "O campo 'dias_adicionais' é obrigatório."}), 400

        dias_adicionais = int(data['dias_adicionais'])
        if dias_adicionais <= 0 or dias_adicionais > 30:
            return jsonify({"erro": "O período de renovação deve ser entre 1 e 30 dias."}), 400

        aluguel = session.query(Aluguel).get(id)
        if not aluguel or aluguel.id_cliente != cliente.id_usuario:
            return jsonify({"erro": "Aluguel não encontrado ou não pertence a este cliente."}), 404

        if aluguel.status == 'FINALIZADO':
            return jsonify({"erro": "Não é possível renovar um aluguel já finalizado."}), 400

        # Para renovar, pega o valor da diária atual do jogo
        item_transacao = session.query(ItemTransacao).filter_by(id_transacao=aluguel.id).first()
        exemplar = session.query(Exemplar).get(item_transacao.id_exemplar)
        jogo = session.query(Jogo).get(exemplar.id_jogo)

        acrescimo = jogo.valor_diaria_aluguel * dias_adicionais
        aluguel.periodo += dias_adicionais
        aluguel.data_prevista_devolucao += timedelta(days=dias_adicionais)
        aluguel.valor_total += acrescimo

        session.commit()
        logger.info(f"Cliente ID {cliente.id_usuario} RENOVOU o aluguel ID {aluguel.id} por mais {dias_adicionais} dias.")
        return jsonify({
            "mensagem": "Aluguel renovado com sucesso.",
            "nova_data_devolucao": aluguel.data_prevista_devolucao.isoformat(),
            "novo_valor_total": float(aluguel.valor_total)
        }), 200

    except Exception as e:
        session.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()
