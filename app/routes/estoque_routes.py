import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from app.models import Catalogo, Exemplar, MidiaFisica, MidiaDigital, Funcionario
from app.database.factories.database_manager import DatabaseManager

estoque_bp = Blueprint('estoque', __name__, url_prefix='/api/estoque')

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_funcionario_from_header(session):
    """Verifica se o header X-Funcionario-Id foi passado e se é um funcionário válido."""
    func_id = request.headers.get('X-Funcionario-Id')
    
    # Faz fallback para X-Admin-Id caso alguém envie como admin
    if not func_id:
        func_id = request.headers.get('X-Admin-Id')
        
    if not func_id:
        return None, "Header X-Funcionario-Id (ou X-Admin-Id) é obrigatório para esta operação."
    
    try:
        func_id = int(func_id)
    except ValueError:
        return None, "O ID do funcionário deve ser um número inteiro."

    funcionario = session.query(Funcionario).get(func_id)
    if not funcionario:
        return None, "Funcionário não encontrado."
        
    return funcionario, None


def serialize_exemplar(exemplar: Exemplar):
    """Serializa um Exemplar baseando-se no seu tipo real (Físico ou Digital)."""
    base_data = {
        "id": exemplar.id,
        "id_catalogo": exemplar.id_catalogo,
        "tipo_midia": exemplar.tipo_midia
    }
    
    if isinstance(exemplar, MidiaFisica):
        base_data.update({
            "codigo_barras": exemplar.codigo_barras,
            "estado_conservacao": exemplar.estado_conservacao
        })
    elif isinstance(exemplar, MidiaDigital):
        base_data.update({
            "chave_ativacao": exemplar.chave_ativacao,
            "data_expiracao": exemplar.data_expiracao.isoformat() if exemplar.data_expiracao else None
        })
        
    return base_data


# ==========================================
# CREATE (C) - Cadastro de Mídia Física
# ==========================================
@estoque_bp.route('/fisico', methods=['POST'])
def cadastrar_midia_fisica():
    session = DatabaseManager.get_session()
    try:
        funcionario, erro = get_funcionario_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        data = request.get_json()
        if not data: return jsonify({"erro": "Dados não fornecidos."}), 400

        required_fields = ['id_catalogo', 'codigo_barras', 'estado_conservacao']
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return jsonify({"erro": f"O campo '{field}' é obrigatório."}), 400

        catalogo = session.query(Catalogo).get(data['id_catalogo'])
        if not catalogo:
            return jsonify({"erro": "Jogo não encontrado no catálogo."}), 404

        # Prevenção de duplicidade
        codigo_existe = session.query(MidiaFisica).filter_by(codigo_barras=data['codigo_barras']).first()
        if codigo_existe:
            return jsonify({"erro": f"O código de barras '{data['codigo_barras']}' já está cadastrado no sistema."}), 400

        nova_midia = MidiaFisica(
            id_catalogo=catalogo.id,
            codigo_barras=data['codigo_barras'],
            estado_conservacao=data['estado_conservacao']
        )

        session.add(nova_midia)
        session.commit()

        logger.info(f"Funcionário ID {funcionario.id_usuario} cadastrou mídia FÍSICA '{nova_midia.codigo_barras}' para o jogo '{catalogo.titulo}'.")
        return jsonify(serialize_exemplar(nova_midia)), 201

    except IntegrityError:
        session.rollback()
        return jsonify({"erro": "Erro de integridade ao salvar no banco."}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        session.close()


# ==========================================
# CREATE (C) - Cadastro de Mídia Digital
# ==========================================
@estoque_bp.route('/digital', methods=['POST'])
def cadastrar_midia_digital():
    session = DatabaseManager.get_session()
    try:
        funcionario, erro = get_funcionario_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        data = request.get_json()
        if not data: return jsonify({"erro": "Dados não fornecidos."}), 400

        required_fields = ['id_catalogo', 'chave_ativacao']
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return jsonify({"erro": f"O campo '{field}' é obrigatório."}), 400

        catalogo = session.query(Catalogo).get(data['id_catalogo'])
        if not catalogo:
            return jsonify({"erro": "Jogo não encontrado no catálogo."}), 404

        # Prevenção de duplicidade
        chave_existe = session.query(MidiaDigital).filter_by(chave_ativacao=data['chave_ativacao']).first()
        if chave_existe:
            return jsonify({"erro": "Esta chave de ativação já está cadastrada no sistema."}), 400

        data_expiracao = None
        if 'data_expiracao' in data and data['data_expiracao']:
            try:
                data_expiracao = datetime.strptime(data['data_expiracao'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"erro": "Formato de data inválido. Use AAAA-MM-DD."}), 400

        nova_midia = MidiaDigital(
            id_catalogo=catalogo.id,
            chave_ativacao=data['chave_ativacao'],
            data_expiracao=data_expiracao
        )

        session.add(nova_midia)
        session.commit()

        logger.info(f"Funcionário ID {funcionario.id_usuario} cadastrou mídia DIGITAL para o catalogo '{catalogo.titulo}'.")
        return jsonify(serialize_exemplar(nova_midia)), 201

    except IntegrityError:
        session.rollback()
        return jsonify({"erro": "Erro de integridade ao salvar no banco."}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        session.close()


# ==========================================
# READ ALL (R) - Lista o estoque de um Jogo
# ==========================================
@estoque_bp.route('/catalogo/<int:id_catalogo>', methods=['GET'])
def listar_estoque_do_catalogo(id_catalogo):
    session = DatabaseManager.get_session()
    try:
        catalogo = session.query(Catalogo).get(id_catalogo)
        if not catalogo:
            return jsonify({"erro": "Jogo não encontrado no catálogo."}), 404

        # Consulta baseada no relacionamento de Herança
        exemplares = session.query(Exemplar).filter_by(id_catalogo=id_catalogo).all()
        
        return jsonify([serialize_exemplar(ex) for ex in exemplares]), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar estoque: {str(e)}"}), 500
    finally:
        session.close()


# ==========================================
# UPDATE (U) - Atualizar estado de conservação
# ==========================================
@estoque_bp.route('/fisico/<int:id>', methods=['PUT'])
def atualizar_estado_fisico(id):
    session = DatabaseManager.get_session()
    try:
        funcionario, erro = get_funcionario_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        data = request.get_json()
        if not data or 'estado_conservacao' not in data:
            return jsonify({"erro": "O campo 'estado_conservacao' é obrigatório."}), 400

        midia = session.query(MidiaFisica).get(id)
        if not midia:
            return jsonify({"erro": "Exemplar físico não encontrado."}), 404

        estado_antigo = midia.estado_conservacao
        midia.estado_conservacao = data['estado_conservacao']
        
        session.commit()

        logger.info(f"Funcionário ID {funcionario.id_usuario} ATUALIZOU o estado da mídia {midia.codigo_barras} de '{estado_antigo}' para '{midia.estado_conservacao}'.")
        return jsonify(serialize_exemplar(midia)), 200

    except Exception as e:
        session.rollback()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        session.close()


# ==========================================
# DELETE (D) - Exclusão de Exemplar
# ==========================================
@estoque_bp.route('/<int:id>', methods=['DELETE'])
def excluir_exemplar(id):
    session = DatabaseManager.get_session()
    try:
        funcionario, erro = get_funcionario_from_header(session)
        if erro: return jsonify({"erro": erro}), 403

        exemplar = session.query(Exemplar).get(id)
        if not exemplar:
            return jsonify({"erro": "Exemplar não encontrado."}), 404

        tipo = exemplar.tipo_midia
        session.delete(exemplar)
        session.commit()
        
        logger.warning(f"Funcionário ID {funcionario.id_usuario} EXCLUIU o exemplar ID {id} ({tipo}).")
        return jsonify({"mensagem": "Exemplar excluído do estoque com sucesso."}), 200
        
    except IntegrityError:
        session.rollback()
        # Se houver uma transação vinculada a este exemplar, a FK impedirá a exclusão.
        return jsonify({"erro": "Não é possível excluir este exemplar pois existem transações atreladas a ele (venda ou aluguel histórico)."}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"erro": f"Erro ao excluir exemplar: {str(e)}"}), 500
    finally:
        session.close()
