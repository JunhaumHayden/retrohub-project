from flask_restx import Namespace, Resource

from app.container.container import container
from app.models import Cliente, Funcionario, Aluguel


demo_ns = Namespace('demo', description='Demo helpers', path='/api/demo')


@demo_ns.route('/available')
class DemoAvailableResource(Resource):
    def get(self):
        """Return available demo IDs and simple info to help presenters"""
        try:
            clientes = container.data_source.get_all(Cliente)
            funcionarios = container.data_source.get_all(Funcionario)
            alugueis = container.data_source.get_all(Aluguel)

            return {
                'clientes': [getattr(c, 'id_usuario', getattr(c, 'id', None)) for c in clientes],
                'funcionarios': [getattr(f, 'id_usuario', getattr(f, 'id', None)) for f in funcionarios],
                'alugueis': [{'id': a.id, 'status': getattr(a, 'status', None), 'id_cliente': getattr(a, 'id_cliente', None)} for a in alugueis]
            }, 200
        except Exception:
            return {'erro': 'Não foi possível recuperar dados de demonstração.'}, 500


@demo_ns.route('/reset')
class DemoResetResource(Resource):
    def post(self):
        """Reload mock data from resources/database/data-mock.json into the running MockDataSource."""
        try:
            ds = container.data_source
            if hasattr(ds, 'load_data'):
                ds.load_data()
                alugueis = ds.get_all(Aluguel)
                return {
                    'mensagem': 'Dados de mock recarregados com sucesso.',
                    'alugueis': [{'id': a.id, 'status': getattr(a, 'status', None)} for a in alugueis]
                }, 200
            return {'erro': 'Fonte de dados não suporta recarga.'}, 500
        except Exception:
            return {'erro': 'Falha ao recarregar dados de mock.'}, 500
