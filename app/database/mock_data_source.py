# app/database/mock/mock_data_source.py
import json
import os
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Type, Any, TypeVar

from app.models.usuario.usuario import Usuario
from app.models.usuario.cliente import Cliente
from app.models.usuario.funcionario import Funcionario
from app.models.catalogo.catalogo import Catalogo
from app.models.estoque.exemplar import Exemplar
from app.models.estoque.midia_fisica import MidiaFisica
from app.models.estoque.midia_digital import MidiaDigital
from app.models.base import CatalogoReference
from app.models.transacao.transacao import Transacao
from app.models.transacao.venda.venda import Venda
from app.models.transacao.aluguel.aluguel import Aluguel
from app.models.transacao.aluguel.reserva import Reserva
from app.models.transacao.aluguel.multa import Multa
from app.models.transacao.item_transacao import ItemTransacao
from app.models.transacao.avaliacao import Avaliacao
from app.models.transacao.comprovante import Comprovante
from app.database.interfaces.data_source_interface import DataSourceInterface

T = TypeVar('T')

class MockDataSource(DataSourceInterface):
    """Mock data source that loads data from a JSON file and creates model instances in memory.
    Provides CRUD operations for all entity types.
    """

    def __init__(self):
        self._data: Dict[str, List[Any]] = {}
        self._loaded = False
        self._relations_built = False
        self._id_counters: Dict[str, int] = {}
        self._entity_type_mapping: Dict[str, Type] = {
            'usuarios': Usuario,
            'clientes': Cliente,
            'funcionarios': Funcionario,
            'catalogo': Catalogo,
            'exemplares': Exemplar,
            'midias_fisicas': MidiaFisica,
            'midias_digitais': MidiaDigital,
            'reservas': Reserva,
            'transacoes': Transacao,
            'vendas': Venda,
            'alugueis': Aluguel,
            'itens_transacao': ItemTransacao,
            'comprovantes': Comprovante,
            'multas': Multa,
            'avaliacoes': Avaliacao
        }

    def load_data(self) -> None:
        """Load initial data from JSON file into memory"""
        if self._loaded:
            return

        json_data = self._load_json_data()

        # Load all entity types
        self._data["clientes"] = self._create_clientes(json_data.get("clientes", []))
        self._data["funcionarios"] = self._create_funcionarios(json_data.get("funcionarios", []))
        self._data["catalogo"] = self._create_catalogo(json_data.get("catalogo", []))
        self._data["transacoes"] = self._create_transacoes(json_data.get("transacoes", []))
        self._data["exemplares"] = []  # Abstract class, created through midias
        self._data["midias_fisicas"] = self._create_midias_fisicas(json_data.get("midias_fisicas", []))
        self._data["midias_digitais"] = self._create_midias_digitais(json_data.get("midias_digitais", []))
        self._data["reservas"] = self._create_reservas(json_data.get("reservas", []))
        self._data["vendas"] = self._create_vendas(json_data.get("vendas", []))
        self._data["alugueis"] = self._create_alugueis(json_data.get("alugueis", []))
        self._data["itens_transacao"] = self._create_itens_transacao(json_data.get("itens_transacao", []))
        self._data["comprovantes"] = self._create_comprovantes(json_data.get("comprovantes", []))
        self._data["multas"] = self._create_multas(json_data.get("multas", []))
        self._data["avaliacoes"] = self._create_avaliacoes(json_data.get("avaliacoes", []))
        
        # Initialize ID counters based on loaded data
        self._initialize_id_counters()
        
        # Build relationships between entities
        self._build_relations()
        
        self._loaded = True

    def _load_json_data(self) -> Dict[str, List[Dict]]:
        """Load data from JSON mock file"""
        json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'database', 'data-mock.json')

        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
        return datetime.strptime(date_str, '%Y-%m-%d').date()

    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not datetime_str:
            return None
        try:
            # Try full datetime format first
            return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # Try date only format
                date_obj = datetime.strptime(datetime_str, '%Y-%m-%d').date()
                # Convert to datetime at midnight
                return datetime.combine(date_obj, datetime.min.time())
            except ValueError:
                return None

    def _parse_decimal(self, value: Optional[Any]) -> Optional[Decimal]:
        """Parse value to Decimal"""
        if value is None:
            return None
        return Decimal(str(value))

    def _ensure_cache_loaded(self):
        """Ensure data is loaded into cache"""
        if not self._data_cache:
            json_data = self._load_json_data()

            # Load all entities
            self._data_cache['usuarios'] = self._create_usuarios(json_data.get('usuarios', []))
            self._data_cache['funcionarios'] = self._create_funcionarios(json_data.get('funcionarios', []))
            self._data_cache['clientes'] = self._create_clientes(json_data.get('clientes', []))
            self._data_cache['catalogo'] = self._create_catalogo(json_data.get('catalogo', []))
            self._data_cache['exemplares'] = self._create_exemplares(json_data.get('exemplares', []))
            self._data_cache['midias_fisicas'] = self._create_midias_fisicas(json_data.get('midias_fisicas', []))
            self._data_cache['midias_digitais'] = self._create_midias_digitais(json_data.get('midias_digitais', []))
            self._data_cache['reservas'] = self._create_reservas(json_data.get('reservas', []))
            self._data_cache['transacoes'] = self._create_transacoes(json_data.get('transacoes', []))
            self._data_cache['vendas'] = self._create_vendas(json_data.get('vendas', []))
            self._data_cache['alugueis'] = self._create_alugueis(json_data.get('alugueis', []))
            self._data_cache['itens_transacao'] = self._create_itens_transacao(json_data.get('itens_transacao', []))
            self._data_cache['comprovantes'] = self._create_comprovantes(json_data.get('comprovantes', []))
            self._data_cache['multas'] = self._create_multas(json_data.get('multas', []))
            self._data_cache['avaliacoes'] = self._create_avaliacoes(json_data.get('avaliacoes', []))

    def _build_relations(self):
        """Resolve todas as chaves estrangeiras pendentes em referências reais.

        Esse método é chamado depois que TODAS as entidades foram instanciadas
        em ``load_data``. Ele lê os atributos ``_pending_id_*`` que foram
        marcados pelos métodos ``_create_*`` e popula os atributos de
        navegação (``cliente``, ``funcionario``, ``transacao``, etc.) com os
        objetos correspondentes.
        """
        if getattr(self, "_relations_built", False):
            return

        # Índices auxiliares por id, para lookup O(1)
        catalogo_dict = {c.id: c for c in self._data["catalogo"]}
        cliente_dict = {c.id: c for c in self._data["clientes"]}
        funcionario_dict = {f.id: f for f in self._data["funcionarios"]}
        venda_dict = {v.id: v for v in self._data["vendas"]}
        aluguel_dict = {a.id: a for a in self._data["alugueis"]}
        reserva_dict = {r.id: r for r in self._data["reservas"]}

        # Vista unificada de transações: vendas ∪ aluguéis (ambas extends Transacao).
        transacao_dict = {**venda_dict, **aluguel_dict}

        midias_fisicas = self._data["midias_fisicas"]
        midias_digitais = self._data["midias_digitais"]
        exemplar_dict = {m.id: m for m in (*midias_fisicas, *midias_digitais)}

        for midia in (*midias_fisicas, *midias_digitais):
            if hasattr(midia, 'catalogo_ref') and midia.catalogo_ref:
                catalogo = catalogo_dict.get(midia.catalogo_ref.id)
                if catalogo:
                    midia.catalogo_ref.set_catalogo(catalogo)
                    catalogo.add_exemplar(midia)

        for reserva in self._data["reservas"]:
            reserva.cliente = cliente_dict.get(
                getattr(reserva, "_pending_id_cliente", None)
            )
            reserva.catalogo = catalogo_dict.get(
                getattr(reserva, "_pending_id_catalogo", None)
            )

        for transacao in (*self._data["vendas"], *self._data["alugueis"]):
            transacao.cliente = cliente_dict.get(
                getattr(transacao, "_pending_id_cliente", None)
            )
            transacao.funcionario = funcionario_dict.get(
                getattr(transacao, "_pending_id_funcionario", None)
            )

        for aluguel in self._data["alugueis"]:
            aluguel.reserva = reserva_dict.get(
                getattr(aluguel, "_pending_id_reserva", None)
            )

        for item in self._data["itens_transacao"]:
            transacao = transacao_dict.get(
                getattr(item, "_pending_id_transacao", None)
            )
            exemplar = exemplar_dict.get(
                getattr(item, "_pending_id_exemplar", None)
            )
            item.exemplar = exemplar
            if transacao is not None:
                transacao.adicionar_item(item)

        for comprovante in self._data["comprovantes"]:
            transacao = transacao_dict.get(
                getattr(comprovante, "_pending_id_transacao", None)
            )
            if transacao is not None:
                transacao.adicionar_comprovante(comprovante)

        for avaliacao in self._data["avaliacoes"]:
            transacao = transacao_dict.get(
                getattr(avaliacao, "_pending_id_transacao", None)
            )
            avaliacao.transacao = transacao
            if transacao is not None:
                transacao.avaliacao = avaliacao

        for multa in self._data["multas"]:
            aluguel = aluguel_dict.get(
                getattr(multa, "_pending_id_aluguel", None)
            )
            multa.aluguel = aluguel
            if aluguel is not None:
                aluguel.multa_aplicada = multa

        # Mantém a chave "transacoes" como visão unificada para consultas
        # genéricas via get_all(Transacao).
        self._data["transacoes"] = list(transacao_dict.values())

        self._relations_built = True

    def _create_usuarios(self, usuarios_data: List[Dict]) -> List[Usuario]:
        """Create Usuario objects"""
        # Note: We don't create Usuario objects directly since Usuario is an abstract class
        # that prevents direct instantiation. Usuarios are created through Cliente and Funcionario subclasses.
        return []

    def _create_funcionarios(self, funcionarios_data: List[Dict]) -> List[Funcionario]:
        """Create Funcionario objects"""
        funcionarios = []
        # First load usuarios data to get base user information
        usuarios_data = self._load_json_data().get('usuarios', [])
        usuarios_dict = {u['id']: u for u in usuarios_data}

        for data in funcionarios_data:
            usuario_data = usuarios_dict.get(data['id_usuario'])
            if usuario_data:
                funcionario = Funcionario(
                    matricula=data['matricula'],
                    id_usuario=data['id_usuario'],
                    nome=usuario_data['nome'],
                    cpf=usuario_data['cpf'],
                    email=usuario_data['email'],
                    senha=usuario_data['senha'],
                    data_nascimento=self._parse_date(usuario_data.get('data_nascimento')),
                    cargo=data.get('cargo'),
                    setor=data.get('setor'),
                    data_admissao=self._parse_date(data.get('data_admissao'))
                )
                funcionarios.append(funcionario)
        return funcionarios

    def _create_clientes(self, clientes_data: List[Dict]) -> List[Cliente]:
        """Create Cliente objects"""
        clientes = []
        # First load usuarios data to get base user information
        usuarios_data = self._load_json_data().get('usuarios', [])
        usuarios_dict = {u['id']: u for u in usuarios_data}

        for data in clientes_data:
            usuario_data = usuarios_dict.get(data['id_usuario'])
            if usuario_data:
                cliente = Cliente(
                    id_usuario=data['id_usuario'],
                    nome=usuario_data['nome'],
                    cpf=usuario_data['cpf'],
                    email=usuario_data['email'],
                    senha=usuario_data['senha'],
                    data_nascimento=self._parse_date(usuario_data.get('data_nascimento')),
                    dados_pagamento=data.get('dados_pagamento'),
                    tipo_cliente=data.get('tipo_cliente')
                )
                clientes.append(cliente)
        return clientes

    def _create_catalogo(self, catalogo_data: List[Dict]) -> List[Catalogo]:
        """Create Catalogo objects"""
        catalogos = []
        for data in catalogo_data:
            catalogo = Catalogo(
                id=data['id'],
                titulo=data['titulo'],
                situacao=data.get('situacao'),
                descricao=data.get('descricao'),
                genero=data.get('genero'),
                classificacao=data.get('classificacao')
            )
            catalogos.append(catalogo)
        return catalogos

    def _create_exemplares(self, exemplares_data: List[Dict]) -> List[Exemplar]:
        """Create Exemplar objects"""
        # Note: We don't create Exemplar objects directly since Exemplar is an abstract class
        # that prevents direct instantiation. Exemplar are created through MidiaFisica and MidiaDigital subclasses.
        return []

    def _create_midias_fisicas(self, midias_data: List[Dict]) -> List[MidiaFisica]:
        """Create MidiaFisica objects"""
        midias = []
        # First load exemplares data to get catalogo information
        exemplares_data = self._load_json_data().get('exemplares', [])
        exemplares_dict = {e['id']: e for e in exemplares_data}

        for data in midias_data:
            exemplar_data = exemplares_dict.get(data['id_exemplar'])
            if exemplar_data:
                # Create catalogo reference instead of passing catalogo object
                catalogo_ref = CatalogoReference(exemplar_data['id_catalogo'])
                midia = MidiaFisica(
                    id_exemplar=data['id_exemplar'],
                    codigo_barras=data['codigo_barras'],
                    catalogo=catalogo_ref,
                    estado_conservacao=data.get('estado_conservacao'),
                    plataforma=data.get('plataforma'),
                    valor_venda=self._parse_decimal(data.get('valor_venda')),
                    valor_diaria_aluguel=self._parse_decimal(
                        data.get('valor_diaria_aluguel')
                    ),
                )
                midias.append(midia)
        return midias

    def _create_midias_digitais(self, midias_data: List[Dict]) -> List[MidiaDigital]:
        """Create MidiaDigital objects"""
        midias = []
        # First load exemplares data to get catalogo information
        exemplares_data = self._load_json_data().get('exemplares', [])
        exemplares_dict = {e['id']: e for e in exemplares_data}

        for data in midias_data:
            exemplar_data = exemplares_dict.get(data['id_exemplar'])
            if exemplar_data:
                # Create catalogo reference instead of passing catalogo object
                catalogo_ref = CatalogoReference(exemplar_data['id_catalogo'])
                midia = MidiaDigital(
                    id_exemplar=data['id_exemplar'],
                    chave_ativacao=data['chave_ativacao'],
                    catalogo=catalogo_ref,
                    data_expiracao=self._parse_date(data.get('data_expiracao')),
                    plataforma=data.get('plataforma'),
                    valor_venda=self._parse_decimal(data.get('valor_venda')),
                    valor_diaria_aluguel=self._parse_decimal(
                        data.get('valor_diaria_aluguel')
                    ),
                )
                midias.append(midia)
        return midias

    def _create_reservas(self, reservas_data: List[Dict]) -> List[Reserva]:
        """Create Reserva objects.

        Os IDs estrangeiros (cliente, catalogo) são armazenados em atributos
        privados (``_pending_id_*``) para serem resolvidos em
        ``_build_relations`` após o carregamento completo.
        """
        reservas = []
        for data in reservas_data:
            reserva = Reserva(
                id=data['id'],
                status=data.get('status'),
                data_reserva=self._parse_date(data.get('data_reserva')),
                data_expiracao=self._parse_date(data.get('data_expiracao')),
            )
            reserva._pending_id_cliente = data.get('id_cliente')
            reserva._pending_id_catalogo = data.get('id_catalogo')
            reservas.append(reserva)
        return reservas

    def _create_transacoes(self, transacoes_data: List[Dict]) -> List[Transacao]:
        """Não cria nada: as transações são instanciadas em
        ``_create_vendas`` e ``_create_alugueis`` (subclasses concretas).

        Mantemos o método para compatibilidade com ``load_data``, mas o
        índice ``self._data["transacoes"]`` é populado em ``_build_relations``
        como a união das vendas e aluguéis.
        """
        return []

    def _create_vendas(self, vendas_data: List[Dict]) -> List[Venda]:
        """Cria objetos Venda a partir do JSON.

        Combina os dados específicos de venda (status, data_confirmacao) com
        os dados base da transação correspondente (id_cliente, valor_total,
        etc.) usando o ``id_transacao`` como chave.
        """
        transacoes_dict = {
            t['id']: t for t in self._load_json_data().get('transacoes', [])
        }

        vendas = []
        for data in vendas_data:
            transacao_data = transacoes_dict.get(data['id_transacao'], {})
            venda = Venda(
                id_transacao=data['id_transacao'],
                status=data.get('status'),
                data_confirmacao=self._parse_date(data.get('data_confirmacao')),
                valor_total=self._parse_decimal(transacao_data.get('valor_total')),
                data_transacao=self._parse_datetime(transacao_data.get('data_transacao')),
                status_pagamento=transacao_data.get('status_pagamento'),
            )
            venda._pending_id_cliente = transacao_data.get('id_cliente')
            venda._pending_id_funcionario = transacao_data.get('id_funcionario')
            vendas.append(venda)
        return vendas

    def _create_alugueis(self, alugueis_data: List[Dict]) -> List[Aluguel]:
        """Cria objetos Aluguel combinando dados específicos de aluguel com
        os dados base da transação correspondente.
        """
        transacoes_dict = {
            t['id']: t for t in self._load_json_data().get('transacoes', [])
        }

        alugueis = []
        for data in alugueis_data:
            transacao_data = transacoes_dict.get(data['id_transacao'], {})
            aluguel = Aluguel(
                id_transacao=data['id_transacao'],
                valor_total=self._parse_decimal(transacao_data.get('valor_total')),
                data_transacao=self._parse_datetime(transacao_data.get('data_transacao')),
                status_pagamento=transacao_data.get('status_pagamento'),
                periodo=data.get('periodo'),
                data_devolucao=self._parse_date(data.get('data_devolucao')),
                status=data.get('status'),
                data_inicio=self._parse_date(data.get('data_inicio')),
                data_prevista_devolucao=self._parse_date(
                    data.get('data_prevista_devolucao')
                ),
            )
            aluguel._pending_id_cliente = transacao_data.get('id_cliente')
            aluguel._pending_id_funcionario = transacao_data.get('id_funcionario')
            aluguel._pending_id_reserva = data.get('id_reserva')
            alugueis.append(aluguel)
        return alugueis

    def _create_itens_transacao(self, itens_data: List[Dict]) -> List[ItemTransacao]:
        """Cria objetos ItemTransacao com FKs pendentes."""
        itens = []
        for data in itens_data:
            item = ItemTransacao(
                id=data.get('id'),
                valor_unitario=self._parse_decimal(data.get('valor_unitario')),
                quantidade=data.get('quantidade', 1),
            )
            item._pending_id_transacao = data.get('id_transacao')
            item._pending_id_exemplar = data.get('id_exemplar')
            itens.append(item)
        return itens

    def _create_comprovantes(self, comprovantes_data: List[Dict]) -> List[Comprovante]:
        """Cria objetos Comprovante com FK ``id_transacao`` pendente."""
        comprovantes = []
        for data in comprovantes_data:
            comprovante = Comprovante(
                id=data.get('id'),
                tipo=data.get('tipo'),
                data_envio=self._parse_datetime(data.get('data_envio')),
                tipo_comprovante=data.get('tipo_comprovante'),
                codigo_rastreio=data.get('codigo_rastreio'),
            )
            comprovante._pending_id_transacao = data.get('id_transacao')
            comprovantes.append(comprovante)
        return comprovantes

    def _create_multas(self, multas_data: List[Dict]) -> List[Multa]:
        """Cria objetos Multa.

        Se a multa estiver vinculada a um aluguel (campo ``id_aluguel`` no
        JSON), mantém a FK pendente para resolução posterior.
        """
        multas = []
        for data in multas_data:
            multa = Multa(
                id=data.get('id'),
                dias_atraso=data.get('dias_atraso'),
                valor=self._parse_decimal(data.get('valor')),
                status=data.get('status'),
                data_calculo=self._parse_date(data.get('data_calculo')),
            )
            multa._pending_id_aluguel = data.get('id_aluguel')
            multas.append(multa)
        return multas

    def _create_avaliacoes(self, avaliacoes_data: List[Dict]) -> List[Avaliacao]:
        """Cria objetos Avaliacao com FK ``id_transacao`` pendente."""
        avaliacoes = []
        for data in avaliacoes_data:
            avaliacao = Avaliacao(
                id=data.get('id'),
                nota=data.get('nota'),
                comentario=data.get('comentario'),
                data_avaliacao=self._parse_date(data.get('data_avaliacao')),
            )
            avaliacao._pending_id_transacao = data.get('id_transacao')
            avaliacoes.append(avaliacao)
        return avaliacoes

    def _initialize_id_counters(self) -> None:
        """Inicializa o contador de IDs por tipo de entidade.

        Trata entidades sem ``id`` (ou ``id is None``) como id=0, evitando
        ``TypeError`` ao comparar ``None`` no ``max(...)``.
        """
        for entity_type, entities in self._data.items():
            ids = [getattr(e, 'id', None) or 0 for e in entities]
            self._id_counters[entity_type] = max(ids) if ids else 0

    def _get_entity_key(self, entity_type: Type[T]) -> str:
        """Retorna a chave de armazenamento para um tipo de entidade.

        Faz duas passagens: primeiro busca correspondência EXATA de tipo
        (para diferenciar ``Cliente`` de ``Usuario``, ``Venda`` de
        ``Transacao``, etc.), só então cai para correspondência por
        subclasse. Sem isso, ``Cliente`` resolveria para a chave
        ``"usuarios"`` (que não é onde clientes ficam armazenados).
        """
        for key, mapped_type in self._entity_type_mapping.items():
            if mapped_type is entity_type:
                return key
        for key, mapped_type in self._entity_type_mapping.items():
            try:
                if issubclass(entity_type, mapped_type):
                    return key
            except TypeError:
                continue
        raise ValueError(f"Unknown entity type: {entity_type}")

    def get_all(self, entity_type: Type[T]) -> List[T]:
        """Get all entities of a specific type.

        Casos especiais (abstratos):
        - ``Exemplar`` -> união de ``midias_fisicas`` + ``midias_digitais``.
        - ``Transacao`` -> união de ``vendas`` + ``alugueis``.
        - ``Usuario`` -> união de ``clientes`` + ``funcionarios``.
        """
        self._ensure_loaded()
        if entity_type is Exemplar:
            return [
                *self._data.get('midias_fisicas', []),
                *self._data.get('midias_digitais', []),
            ]
        if entity_type is Transacao:
            return [
                *self._data.get('vendas', []),
                *self._data.get('alugueis', []),
            ]
        if entity_type is Usuario:
            return [
                *self._data.get('clientes', []),
                *self._data.get('funcionarios', []),
            ]
        key = self._get_entity_key(entity_type)
        return self._data.get(key, [])

    def get_by_id(self, entity_type: Type[T], entity_id: int) -> Optional[T]:
        """Get entity by ID and type"""
        self._ensure_loaded()
        entities = self.get_all(entity_type)
        for entity in entities:
            if hasattr(entity, 'id') and getattr(entity, 'id') == entity_id:
                return entity
        return None

    def get_by_field(self, entity_type: Type[T], field_name: str, value) -> Optional[T]:
        """Get entity by field value"""
        self._ensure_loaded()
        entities = self.get_all(entity_type)
        for entity in entities:
            if hasattr(entity, field_name) and getattr(entity, field_name) == value:
                return entity
        return None

    def create(self, entity: T) -> T:
        """Create a new entity"""
        self._ensure_loaded()
        key = self._get_entity_key(type(entity))
        
        # Assign ID if not present
        if not hasattr(entity, 'id') or getattr(entity, 'id') is None:
            entity.id = self.get_next_id(type(entity))
        
        self._data[key].append(entity)
        return entity

    def update(self, entity: T) -> Optional[T]:
        """Update an existing entity"""
        self._ensure_loaded()
        key = self._get_entity_key(type(entity))
        
        if not hasattr(entity, 'id'):
            return None
            
        entities = self._data[key]
        for i, existing_entity in enumerate(entities):
            if hasattr(existing_entity, 'id') and getattr(existing_entity, 'id') == getattr(entity, 'id'):
                entities[i] = entity
                return entity
        return None

    def delete(self, entity_type: Type[T], entity_id: int) -> bool:
        """Delete entity by ID"""
        self._ensure_loaded()
        key = self._get_entity_key(entity_type)
        
        entities = self._data[key]
        for i, entity in enumerate(entities):
            if hasattr(entity, 'id') and getattr(entity, 'id') == entity_id:
                del entities[i]
                return True
        return False

    def get_next_id(self, entity_type: Type[T]) -> int:
        """Get next available ID for entity type"""
        key = self._get_entity_key(entity_type)
        self._id_counters[key] = self._id_counters.get(key, 0) + 1
        return self._id_counters[key]

    def _ensure_loaded(self) -> None:
        """Ensure data is loaded"""
        if not self._loaded:
            self.load_data()

if __name__ == "__main__":
    mock = MockDataSource()
    mock.load_data()
    from app.models.usuario.cliente import Cliente
    clientes = mock.get_all(Cliente)
    print(f"Loaded {len(clientes)} clientes")
    for cliente in clientes[:2]:  # Show first 2
        print(f"Cliente: {cliente.nome} (ID: {cliente.id})")