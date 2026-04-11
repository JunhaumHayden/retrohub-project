import logging
from decimal import Decimal
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from app.models import Jogo, Funcionario
from app.database.factories.database_manager import DatabaseManager

catalogo_bp = Blueprint('catalogo', __name__, url_prefix='/api/catalogo/itens')

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def serialize_jogo(jogo: Jogo):
    """Função utilitária para serializar um objeto Jogo."""
    return {
        "id": jogo.id,
        "titulo": jogo.titulo,
        "descricao": jogo.descricao,
        "plataforma": jogo.plataforma,
        "ativo": jogo.ativo,
        "genero": jogo.genero,
        "classificacao": jogo.classificacao,
        "valor_venda": float(jogo.valor_venda) if jogo.valor_venda else None,
        "valor_diaria_aluguel": float(jogo.valor_diaria_aluguel) if jogo.valor_diaria_aluguel else None
    }

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


# ==========================================
# CREATE (C) - Inserir novo item no catálogo
# ==========================================
@catalogo_bp.route('/', methods=['POST'])
def criar_jogo():
    session = DatabaseManager.get_session()
    try:
        # Apenas Funcionários (ou Admin) podem cadastrar
        funcionario, erro = get_funcionario_from_header(session)
        if erro:
            return jsonify({"erro": erro}), 403

        data = request.get_json()
        if not data:
            return jsonify({"erro": "Dados não fornecidos."}), 400

        # Validação de campos obrigatórios
        required_fields = ['titulo', 'plataforma']
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return jsonify({"erro": f"O campo '{field}' é obrigatório."}), 400

        # Prevenção contra duplicidade (título + plataforma)
        jogo_duplicado = session.query(Jogo).filter(
            and_(
                Jogo.titulo.ilike(data['titulo']),
                Jogo.plataforma.ilike(data['plataforma'])
            )
        ).first()
        
        if jogo_duplicado:
            return jsonify({"erro": f"O jogo '{data['titulo']}' já está cadastrado para a plataforma '{data['plataforma']}'."}), 400

        valor_venda = Decimal(str(data['valor_venda'])) if data.get('valor_venda') else None
        valor_diaria_aluguel = Decimal(str(data['valor_diaria_aluguel'])) if data.get('valor_diaria_aluguel') else None

        novo_jogo = Jogo(
            titulo=data['titulo'],
            descricao=data.get('descricao'),
            plataforma=data['plataforma'],
            ativo=data.get('ativo', True),
            genero=data.get('genero'),
            classificacao=data.get('classificacao'),
            valor_venda=valor_venda,
            valor_diaria_aluguel=valor_diaria_aluguel
        )

        session.add(novo_jogo)
        session.commit()

        # Registro de log de criação
        logger.info(f"Funcionário ID {funcionario.id_usuario} ({funcionario.nome}) CADASTROU o jogo '{novo_jogo.titulo}' (ID {novo_jogo.id}).")

        return jsonify(serialize_jogo(novo_jogo)), 201

    except IntegrityError as e:
        session.rollback()
        return jsonify({"erro": "Erro de integridade ao salvar no banco."}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        session.close()


# ==========================================
# READ ALL (R) - Listar jogos
# ==========================================
@catalogo_bp.route('/', methods=['GET'])
def listar_jogos():
    session = DatabaseManager.get_session()
    try:
        # Permite filtrar por status ativo (ex: ?ativo=true)
        ativo_param = request.args.get('ativo')
        query = session.query(Jogo)
        
        if ativo_param is not None:
            is_ativo = ativo_param.lower() == 'true'
            query = query.filter_by(ativo=is_ativo)
            
        jogos = query.all()
        return jsonify([serialize_jogo(j) for j in jogos]), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar catálogo: {str(e)}"}), 500
    finally:
        session.close()


# ==========================================
# READ ONE (R) - Detalhes do jogo
# ==========================================
@catalogo_bp.route('/<int:id>', methods=['GET'])
def buscar_jogo(id):
    session = DatabaseManager.get_session()
    try:
        jogo = session.query(Jogo).get(id)
        if not jogo:
            return jsonify({"erro": "Jogo não encontrado no catálogo."}), 404
            
        return jsonify(serialize_jogo(jogo)), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar jogo: {str(e)}"}), 500
    finally:
        session.close()


# ==========================================
# UPDATE (U) - Atualizar dados do jogo
# ==========================================
@catalogo_bp.route('/<int:id>', methods=['PUT'])
def atualizar_jogo(id):
    session = DatabaseManager.get_session()
    try:
        # Apenas Funcionários podem alterar
        funcionario, erro = get_funcionario_from_header(session)
        if erro:
            return jsonify({"erro": erro}), 403

        data = request.get_json()
        if not data:
            return jsonify({"erro": "Dados não fornecidos."}), 400

        jogo = session.query(Jogo).get(id)
        if not jogo:
            return jsonify({"erro": "Jogo não encontrado."}), 404

        # Prevenção contra duplicidade ao alterar título ou plataforma
        novo_titulo = data.get('titulo', jogo.titulo)
        nova_plataforma = data.get('plataforma', jogo.plataforma)

        if novo_titulo != jogo.titulo or nova_plataforma != jogo.plataforma:
            jogo_duplicado = session.query(Jogo).filter(
                and_(
                    Jogo.titulo.ilike(novo_titulo),
                    Jogo.plataforma.ilike(nova_plataforma),
                    Jogo.id != id
                )
            ).first()
            if jogo_duplicado:
                return jsonify({"erro": f"Já existe outro jogo cadastrado como '{novo_titulo}' na plataforma '{nova_plataforma}'."}), 400

        # Atualização dos campos
        if 'titulo' in data: jogo.titulo = data['titulo']
        if 'descricao' in data: jogo.descricao = data['descricao']
        if 'plataforma' in data: jogo.plataforma = data['plataforma']
        if 'ativo' in data: jogo.ativo = data['ativo']
        if 'genero' in data: jogo.genero = data['genero']
        if 'classificacao' in data: jogo.classificacao = data['classificacao']
        
        if 'valor_venda' in data:
            jogo.valor_venda = Decimal(str(data['valor_venda'])) if data['valor_venda'] is not None else None
            
        if 'valor_diaria_aluguel' in data:
            jogo.valor_diaria_aluguel = Decimal(str(data['valor_diaria_aluguel'])) if data['valor_diaria_aluguel'] is not None else None

        session.commit()

        # Registro de log de alteração
        logger.info(f"Funcionário ID {funcionario.id_usuario} ({funcionario.nome}) ATUALIZOU o jogo '{jogo.titulo}' (ID {jogo.id}).")

        return jsonify(serialize_jogo(jogo)), 200

    except IntegrityError as e:
        session.rollback()
        return jsonify({"erro": "Conflito de dados no banco."}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        session.close()


# ==========================================
# DELETE (D) - Inativar ou Excluir item
# ==========================================
@catalogo_bp.route('/<int:id>', methods=['DELETE'])
def excluir_jogo(id):
    session = DatabaseManager.get_session()
    try:
        funcionario, erro = get_funcionario_from_header(session)
        if erro:
            return jsonify({"erro": erro}), 403

        jogo = session.query(Jogo).get(id)
        if not jogo:
            return jsonify({"erro": "Jogo não encontrado."}), 404

        # Se o jogo já tiver transações/reservas atreladas, a exclusão física (DELETE) vai falhar
        # Para catálogo de produtos, a exclusão lógica (inativação) é sempre a melhor prática
        nome_jogo = jogo.titulo
        jogo.ativo = False
        session.commit()
        
        logger.warning(f"Funcionário ID {funcionario.id_usuario} ({funcionario.nome}) INATIVOU o jogo '{nome_jogo}' (ID {id}).")
        
        return jsonify({"mensagem": "Jogo inativado com sucesso (exclusão lógica).", "jogo": serialize_jogo(jogo)}), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({"erro": f"Erro interno ao excluir jogo: {str(e)}"}), 500
    finally:
        session.close()
