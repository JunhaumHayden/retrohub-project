import logging
from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource, fields

from app.container.container import container

relatorios_ns = Namespace('relatorios', description='Operações de relatórios', path='/api/relatorios')

# Modelos para documentação Swagger
resumo_model = relatorios_ns.model('ResumoRelatorio', {
    'total_vendas': fields.Float(description='Faturamento total com vendas no período'),
    'quantidade_vendas': fields.Integer(description='Número total de vendas no período'),
    'total_alugueis': fields.Float(description='Faturamento total com aluguéis no período'),
    'quantidade_alugueis': fields.Integer(description='Número total de aluguéis no período'),
    'faturamento_total': fields.Float(description='Faturamento consolidado (vendas + aluguéis)'),
})

breakdown_item_model = relatorios_ns.model('BreakdownItem', {
    'quantidade': fields.Integer(description='Quantidade de transações para este item'),
    'valor_total': fields.Float(description='Valor total faturado com este item'),
})

# Register Wildcard model explicitly for dynamic keys
wildcard_breakdown_model = relatorios_ns.model('WildcardBreakdown', {
    '*': fields.Nested(breakdown_item_model, description='Item dinâmico (nome do jogo)')
})

breakdown_model = relatorios_ns.model('BreakdownRelatorio', {
    'vendas': fields.Nested(wildcard_breakdown_model, description='Detalhamento de vendas por jogo'),
    'alugueis': fields.Nested(wildcard_breakdown_model, description='Detalhamento de aluguéis por jogo'),
})

relatorio_completo_model = relatorios_ns.model('RelatorioCompleto', {
    'resumo': fields.Nested(resumo_model),
    'breakdown_por_jogo': fields.Nested(breakdown_model),
})

logger = logging.getLogger(__name__)

def _get_funcionario_from_header():
    func_id = request.headers.get('X-Funcionario-Id') or request.headers.get('X-Admin-Id')
    if not func_id:
        relatorios_ns.abort(403, "Header X-Funcionario-Id (ou X-Admin-Id) é obrigatório.")
    try:
        funcionario = container.usuario_service.get_funcionario_by_id(int(func_id))
        if not funcionario:
            relatorios_ns.abort(403, "Funcionário não encontrado ou não autorizado.")
        return funcionario
    except ValueError:
        relatorios_ns.abort(403, "ID de funcionário inválido.")

@relatorios_ns.route('/compras-locacoes')
class RelatorioComprasLocacoes(Resource):
    @relatorios_ns.doc(params={
        'X-Funcionario-Id': {'in': 'header', 'description': 'ID do funcionário', 'required': True},
        'data_inicio': {'in': 'query', 'description': 'Data de início (YYYY-MM-DD)', 'type': 'string'},
        'data_fim': {'in': 'query', 'description': 'Data de fim (YYYY-MM-DD)', 'type': 'string'}
    })
    @relatorios_ns.marshal_with(relatorio_completo_model)
    def get(self):
        """Gera um relatório de compras e locações com filtros opcionais."""
        _get_funcionario_from_header()
        
        data_inicio_str = request.args.get('data_inicio')
        data_fim_str = request.args.get('data_fim')
        
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date() if data_inicio_str else None
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date() if data_fim_str else None
        except ValueError:
            relatorios_ns.abort(400, "Formato de data inválido. Use AAAA-MM-DD.")
            
        try:
            relatorio = container.relatorio_service.gerar_relatorio_compras_locacoes(data_inicio, data_fim)
            return relatorio
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            relatorios_ns.abort(500, "Erro interno ao gerar o relatório.")
