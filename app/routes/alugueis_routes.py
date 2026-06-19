import logging
from datetime import datetime, timedelta, date
from flask import request
from flask_restx import Namespace, Resource, fields

from app.models import Aluguel
from app.container.container import container

# Criar namespace para aluguéis
alugueis_ns = Namespace('alugueis', description='Operações relacionadas aos aluguéis de jogos', path='/api/alugueis')

# Modelos para documentação Swagger
aluguel_model = alugueis_ns.model('Aluguel', {
    'id': fields.Integer(description='ID do aluguel'),
    'id_cliente': fields.Integer(description='ID do cliente'),
    'id_funcionario': fields.Integer(description='ID do funcionário'),
    'data_solicitacao': fields.Date(description='Data da solicitação'),
    'data_retirada': fields.Date(description='Data da retirada'),
    'data_devolucao_prevista': fields.Date(description='Data de devolução prevista'),
    'data_devolucao_real': fields.Date(description='Data de devolução real'),
    'status': fields.String(description='Status do aluguel'),
    'valor_total': fields.Float(description='Valor total'),
    'multa_atraso': fields.Float(description='Multa por atraso')
})

aluguel_solicitacao_model = alugueis_ns.model('AluguelSolicitacao', {
    'itens': fields.List(fields.Integer, required=True, description='Lista de IDs dos jogos do catálogo'),
    'tipo_midia': fields.String(required=True, description='Tipo de mídia (FISICO ou DIGITAL)')
})

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_cliente_from_header():
    cliente_id = request.headers.get('X-Cliente-Id')
    if not cliente_id:
        return None, "Header X-Cliente-Id é obrigatório."
    try:
        cliente_id = int(cliente_id)
    except ValueError:
        return None, "X-Cliente-Id inválido."
    
    cliente = container.usuario_service.get_cliente_by_id(cliente_id)
    if not cliente:
        return None, "Cliente não cadastrado ou não encontrado."
    
    return cliente, None

def get_funcionario_from_header():
    func_id = request.headers.get('X-Funcionario-Id')
    if not func_id:
        func_id = request.headers.get('X-Admin-Id')
    if not func_id:
        return None, "Header X-Funcionario-Id (ou X-Admin-Id) é obrigatório para esta operação."
    try:
        func_id = int(func_id)
    except ValueError:
        return None, "O ID do funcionário deve ser um número inteiro."
    funcionario = container.usuario_service.get_funcionario_by_id(func_id)
    if not funcionario:
        return None, "Funcionário não encontrado."
    return funcionario, None

def find_exemplar_disponivel(id_catalogo, tipo_midia):
    """Find available exemplar for rental"""
    return container.venda_service.find_exemplar_disponivel_venda(id_catalogo, tipo_midia)

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
        "data_fim_prevista": aluguel.data_prevista_devolucao.isoformat() if aluguel.data_prevista_devolucao else None,
        "data_devolucao": aluguel.data_devolucao.isoformat() if aluguel.data_devolucao else None,
        "data_devolucao_real": aluguel.data_devolucao_real.isoformat() if getattr(aluguel, "data_devolucao_real", None) else None,
        "data_retirada": aluguel.data_retirada.isoformat() if getattr(aluguel, 'data_retirada', None) else None,
        "condicao_item": getattr(aluguel, "condicao_item", None),
        "id_funcionario_recebimento": getattr(aluguel, "id_funcionario_recebimento", None),
        "multa_aplicada": float(aluguel.multa_aplicada) if getattr(aluguel, "multa_aplicada", None) is not None else None,
        "multa_paga": aluguel.multa_paga if getattr(aluguel, "multa_paga", None) is not None else None,
        "dias_atraso": getattr(aluguel, "dias_atraso", None),
        "status_aluguel": getattr(aluguel, 'status', 'ATIVO')
    }


@alugueis_ns.route('/solicitar')
class SolicitarAluguelResource(Resource):
    @alugueis_ns.expect(aluguel_solicitacao_model)
    def post(self):
        """Solicitar um novo aluguel"""
        try:
            cliente, erro = get_cliente_from_header()
            if erro: return {"erro": erro}, 403

            data = request.get_json()
            if not data: return {"erro": "Dados não fornecidos."}, 400

            required_fields = ['id_jogo', 'dias_alugados', 'data_inicio', 'tipo_midia']
            for field in required_fields:
                if field not in data or str(data[field]).strip() == "":
                    return {"erro": f"O campo '{field}' é obrigatório."}, 400

            dias_alugados = int(data['dias_alugados'])
            if dias_alugados <= 0 or dias_alugados > 30:
                return {"erro": "O período de aluguel deve ser entre 1 e 30 dias."}, 400

            try:
                data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d').date()
            except ValueError:
                return {"erro": "Formato de data_inicio inválido. Use AAAA-MM-DD."}, 400

            if data_inicio < date.today():
                return {"erro": "A data de início não pode ser anterior à data atual."}, 400

            jogo = container.catalogo_service.get_by_id(data['id_jogo'])
            if not jogo:
                return {"erro": "Jogo não encontrado no catálogo."}, 404

            if not jogo.valor_diaria_aluguel:
                return {"erro": "Este jogo não está disponível para aluguel (valor da diária não definido)."}, 400

            tipo_midia = str(data['tipo_midia']).upper()
            if tipo_midia not in ['FISICA', 'DIGITAL']:
                return {"erro": "tipo_midia deve ser FISICA ou DIGITAL."}, 400

            # Buscar exemplar disponível
            exemplar_disponivel = find_exemplar_disponivel(jogo.id, tipo_midia)
            if not exemplar_disponivel:
                return {"erro": f"Não há exemplares da mídia {tipo_midia} disponíveis no momento para este jogo."}, 400

            # Calcular valor total
            valor_total = jogo.valor_diaria_aluguel * dias_alugados
            data_prevista_devolucao = data_inicio + timedelta(days=dias_alugados)

            # Note: In mock mode, we can't actually save new rentals
            # This would need to be handled differently in a real implementation
            novo_aluguel = Aluguel(
                id=1,  # Placeholder ID
                id_cliente=cliente.id_usuario,
                valor_total=valor_total,
                status='SOLICITADO',
                data_transacao=datetime.utcnow(),
                periodo=dias_alugados,
                data_inicio=data_inicio,
                data_prevista_devolucao=data_prevista_devolucao
            )
            # In a real implementation, you would save this:
            # MockDataSource.save(novo_aluguel)
            # MockDataSource.save(ItemTransacao(...))

            return {
                "mensagem": "Aluguel solicitado com sucesso!",
                "aluguel": serialize_aluguel(novo_aluguel),
                "exemplar_id": exemplar_disponivel.id
            }, 201

        except Exception as e:
            logger.error(f"Erro em solicitar_aluguel: {str(e)}")
            return {"erro": "Erro interno ao processar solicitação de aluguel."}, 500


@alugueis_ns.route('/meus-alugueis')
class MeusAlugueisResource(Resource):
    def get(self):
        """Listar meus aluguéis"""
        try:
            cliente, erro = get_cliente_from_header()
            if erro: return {"erro": erro}, 403

            from app.models.transacao.aluguel.aluguel import Aluguel
            alugueis = container.aluguel_repository.get_all(Aluguel) if hasattr(container.aluguel_repository, 'get_all') else []
            meus_alugueis = [a for a in alugueis if a.id_cliente == cliente.id_usuario]
            return [serialize_aluguel(a) for a in meus_alugueis], 200

        except Exception as e:
            logger.error(f"Erro em meus_alugueis: {str(e)}")
            return {"erro": "Erro interno ao buscar alugueis."}, 500

@alugueis_ns.route('/<int:id>/retirada')
class RegistrarRetiradaAluguelResource(Resource):
    def patch(self, id):
        """Registrar retirada de aluguel"""
        try:
            _, erro = get_funcionario_from_header()
            if erro:
                return {"erro": erro}, 403

            aluguel, err = container.aluguel_service.registrar_retirada(id)
            if err:
                return {"erro": err}, 400

            logger.info(f"Funcionário registrou retirada do aluguel ID {id}")
            return {
                "mensagem": "Retirada registrada com sucesso.",
                "aluguel": serialize_aluguel(aluguel)
            }, 200

        except Exception as e:
            logger.error(f"Erro em registrar_retirada_aluguel: {str(e)}")
            return {"erro": "Erro interno ao registrar retirada."}, 500

@alugueis_ns.route('/<int:id>/devolucao')
class RegistrarDevolucaoAluguelResource(Resource):
    def patch(self, id):
        """Registrar devolução de aluguel"""
        try:
            funcionario, erro = get_funcionario_from_header()
            if erro:
                return {"erro": erro}, 403

            data = request.get_json()
            if not data:
                return {"erro": "Dados não fornecidos."}, 400
            condicao = data.get("condicao_item")
            aluguel, err = container.aluguel_service.registrar_devolucao(id, condicao, funcionario.id_usuario)
            if err:
                code = 404 if "não encontrado" in err.lower() else 400
                return {"erro": err}, code

            logger.info(f"Devolução registrada para aluguel ID {id}.")
            return serialize_aluguel(aluguel), 200

        except Exception as e:
            logger.error(f"Erro em registrar_devolucao_aluguel: {str(e)}")
            return {"erro": "Erro interno ao registrar devolução."}, 500

@alugueis_ns.route('/<int:id>')
class DetalhesAluguelResource(Resource):
    def get(self, id):
        """Obter detalhes de um aluguel"""
        try:
            cliente, erro = get_cliente_from_header()
            if erro: return {"erro": erro}, 403

            from app.models.transacao.aluguel.aluguel import Aluguel
            aluguel = container.aluguel_repository.get_by_id(Aluguel, id)
            if not aluguel or aluguel.id_cliente != cliente.id_usuario:
                return {"erro": "Aluguel não encontrado ou não pertence a este cliente."}, 404

            return serialize_aluguel(aluguel), 200

        except Exception as e:
            logger.error(f"Erro em detalhes_aluguel: {str(e)}")
            return {"erro": "Erro interno ao buscar detalhes do aluguel."}, 500

@alugueis_ns.route('/<int:id>/cancelar')
class CancelarAluguelResource(Resource):
    def patch(self, id):
        """Cancelar um aluguel"""
        try:
            cliente, erro = get_cliente_from_header()
            if erro: return {"erro": erro}, 403

            from app.models.transacao.aluguel.aluguel import Aluguel
            aluguel = container.aluguel_repository.get_by_id(Aluguel, id)
            if not aluguel or aluguel.id_cliente != cliente.id_usuario:
                return {"erro": "Aluguel não encontrado ou não pertence a este cliente."}, 404

            if aluguel.data_inicio <= date.today():
                return {"erro": "Não é possível cancelar um aluguel que já iniciou ou está no dia de retirada."}, 400

            # Note: In mock mode, we can't actually save changes
            aluguel.status = 'FINALIZADO'
            
            # Find and update the associated item and exemplar
            from app.models.transacao.item_transacao import ItemTransacao
            from app.models.estoque.exemplar import Exemplar
            item_tr = container.venda_repository.get_item_by_transacao(aluguel.id)
            if item_tr:
                exemplar = container.estoque_repository.get_exemplar_by_id(item_tr.id_exemplar)
                if exemplar and exemplar.situacao == 'RESERVADO':
                    exemplar.situacao = 'DISPONIVEL'
                    if hasattr(exemplar, 'codigo_barras'):
                        container.estoque_repository.update_midia_fisica(exemplar)

            # Update aluguel
            container.aluguel_repository.update(aluguel)

            logger.info(f"Cliente ID {cliente.id_usuario} cancelou aluguel ID {id}")
            return {"mensagem": "Aluguel cancelado com sucesso."}, 200

        except Exception as e:
            logger.error(f"Erro em cancelar_aluguel: {str(e)}")
            return {"erro": "Erro interno ao cancelar aluguel."}, 500

@alugueis_ns.route('/<int:id>/renovar')
class RenovarAluguelResource(Resource):
    def patch(self, id):
        """Renovar um aluguel"""
        try:
            cliente, erro = get_cliente_from_header()
            if erro: return {"erro": erro}, 403

            data = request.get_json()
            if not data or 'dias_adicionais' not in data:
                return {"erro": "O campo 'dias_adicionais' é obrigatório."}, 400

            dias_adicionais = int(data['dias_adicionais'])
            if dias_adicionais <= 0 or dias_adicionais > 30:
                return {"erro": "O período de renovação deve ser entre 1 e 30 dias."}, 400

            from app.models.transacao.aluguel.aluguel import Aluguel
            aluguel = container.aluguel_repository.get_by_id(Aluguel, id)
            if not aluguel or aluguel.id_cliente != cliente.id_usuario:
                return {"erro": "Aluguel não encontrado ou não pertence a este cliente."}, 404

            if aluguel.status == 'FINALIZADO':
                return {"erro": "Não é possível renovar um aluguel já finalizado."}, 400

            # Para renovar, pega o valor da diária atual do jogo
            from app.models.transacao.item_transacao import ItemTransacao
            from app.models.estoque.exemplar import Exemplar
            item_transacao = container.venda_repository.get_item_by_transacao(aluguel.id)
            
            if not item_transacao:
                return {"erro": "Item da transação não encontrado."}, 404
                
            exemplar = container.estoque_repository.get_exemplar_by_id(item_transacao.id_exemplar)
            if not exemplar:
                return {"erro": "Exemplar não encontrado."}, 404
                
            jogo = container.catalogo_service.get_by_id(exemplar.id_catalogo)
            if not jogo:
                return {"erro": "Jogo não encontrado."}, 404

            # Note: In mock mode, we can't actually save changes
            acrescimo = jogo.valor_diaria_aluguel * dias_adicionais
            aluguel.periodo += dias_adicionais
            aluguel.data_prevista_devolucao += timedelta(days=dias_adicionais)
            aluguel.valor_total += acrescimo

            # Update aluguel
            container.aluguel_repository.update(aluguel)

            logger.info(f"Cliente ID {cliente.id_usuario} RENOVOU o aluguel ID {aluguel.id} por mais {dias_adicionais} dias.")
            return {
                "mensagem": "Aluguel renovado com sucesso.",
                "nova_data_devolucao": aluguel.data_prevista_devolucao.isoformat(),
                "novo_valor_total": float(aluguel.valor_total)
            }, 200

        except Exception as e:
            logger.error(f"Erro em renovar_aluguel: {str(e)}")
            return {"erro": "Erro interno ao renovar aluguel."}, 500
