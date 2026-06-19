from .clientes_routes import clientes_bp
from .funcionarios_routes import funcionarios_bp
from .catalogo_routes import catalogo_bp
from .estoque_routes import estoque_bp
from .alugueis_routes import alugueis_bp
from .vendas_routes import vendas_bp
from .avaliacoes_routes import avaliacoes_bp
from .relatorios_routes import relatorios_bp

__all__ = [
    'clientes_bp', 'funcionarios_bp', 'catalogo_bp', 'estoque_bp',
    'alugueis_bp', 'vendas_bp', 'avaliacoes_bp', 'relatorios_bp'
]
