# Project Refactoring Documentation

## Overview

This document describes the comprehensive refactoring of the RetroHub project to implement proper layer separation, dependency injection, and a robust mock data system for testing.

## Architecture

### Layer Separation

The project now follows a clean 4-layer architecture:

```
┌─────────────────┐
│   Routes Layer  │ ← Flask-RESTX endpoints, Swagger documentation
├─────────────────┤
│  Service Layer  │ ← Business logic, validation, orchestration
├─────────────────┤
│Repository Layer │ ← Data access abstraction, CRUD operations
├─────────────────┤
│ DataSource Layer│ ← In-memory mock data, interchangeable with DB
└─────────────────┘
```

### Key Components

#### 1. DataSource Layer
- **MockDataSource**: In-memory data manager with full CRUD operations
- **DataSourceInterface**: Abstract interface for data sources
- **JSON Loading**: Initial data loaded from `resources/database/data-mock.json`
- **Entity Management**: Automatic ID generation and relationship building

#### 2. Repository Layer
- **UsuarioRepositoryMock**: User data access (clientes + funcionarios)
- **CatalogoRepositoryMock**: Catalog data access
- **Repository Interfaces**: Abstract contracts for data operations
- **Type Safety**: Generic CRUD operations with type hints

#### 3. Service Layer
- **UsuarioService**: User business logic and validation
- **CatalogoService**: Catalog business logic and validation
- **Error Handling**: Comprehensive validation and error messages
- **Business Rules**: Domain-specific logic implementation

#### 4. Container/Dependency Injection
- **Container**: Singleton dependency management
- **Environment-based**: Switch between mock and real database
- **Lazy Loading**: Components created on first access
- **Testing Support**: Container reset for isolated tests

## Usage

### Environment Configuration

Set `USE_MOCK_DB=true` (default) to use in-memory mock data:
```bash
export USE_MOCK_DB=true
```

### Using the Container

```python
from app.container.container import container

# Access services through dependency injection
usuario_service = container.usuario_service
catalogo_service = container.catalogo_service

# Create entities
cliente = Cliente(nome="Test", cpf="123.456.789-00", email="test@example.com", senha="password")
created_cliente = usuario_service.create_cliente(cliente)

# Query entities
all_clientes = usuario_service.list_clientes()
found_cliente = usuario_service.get_cliente_by_id(created_cliente.id)
```

### Route Layer Integration

Routes now use the service layer instead of direct data access:

```python
from app.container.container import container

@catalogo_ns.route('/')
class CatalogoList(Resource):
    def get(self):
        catalogos = container.catalogo_service.list_all()
        return [serialize_catalogo(c) for c in catalogos]
```

## Testing

### Test Structure

- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component workflow testing
- **Mock Tests**: DataSource and repository testing
- **Service Tests**: Business logic validation testing

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test categories
pytest -m unit
pytest -m integration
```

### Test Files

- `test_mock_data_source.py` - DataSource layer tests
- `test_usuario_repository_mock.py` - Usuario repository tests
- `test_catalogo_service.py` - Catalog service tests
- `test_usuario_service.py` - Usuario service tests
- `test_container.py` - Dependency injection tests
- `test_integration.py` - End-to-end integration tests

## Data Model Changes

### Usuario Hierarchy
```python
Usuario (Abstract)
├── Cliente
└── Funcionario
```

### Catalogo Model
```python
Catalogo
├── id: int
├── titulo: str
├── descricao: str
├── genero: str
├── classificacao: str
├── situacao: str  # DISPONIVEL/INDISPONIVEL
└── exemplares: List[Exemplar]
```

### CRUD Operations

All entities support full CRUD operations:

- **Create**: `service.create(entity)`
- **Read**: `service.get_by_id(id)`, `service.list_all()`
- **Update**: `service.update(id, data)`
- **Delete**: `service.delete(id)`

## Error Handling

### Validation Rules

**Usuario Creation:**
- Nome, CPF, Email, Senha are required
- CPF must be unique across all users
- Email must be unique across all users
- Funcionarios require unique matricula

**Catalogo Creation:**
- Titulo is required
- Titulo must be unique
- Default situacao is DISPONIVEL

### Error Responses

All validation errors return descriptive messages:
```python
# Example: Duplicate CPF
raise ValueError("Cliente com CPF '123.456.789-00' já existe")

# Example: Missing required field
raise ValueError("Nome é obrigatório")
```

## Migration Guide

### Before Refactoring
```python
# Direct data access
from app.database.MockDataSource import MockDataSource

clientes = MockDataSource.get_all(Cliente)
cliente = MockDataSource.get_by_id(Cliente, id)
```

### After Refactoring
```python
# Service layer access
from app.container.container import container

clientes = container.usuario_service.list_clientes()
cliente = container.usuario_service.get_cliente_by_id(id)
```

## Benefits

### 1. Separation of Concerns
- Routes handle HTTP concerns only
- Services contain business logic
- Repositories manage data access
- DataSources handle persistence

### 2. Testability
- Each layer can be tested independently
- Mock data source provides consistent test data
- Dependency injection enables easy mocking

### 3. Maintainability
- Clear boundaries between components
- Single responsibility principle
- Easy to extend and modify

### 4. Scalability
- Services can be easily swapped
- DataSources are interchangeable
- Container manages component lifecycle

## Future Enhancements

### Database Integration
```python
# Future: Real database implementation
class DatabaseDataSource(DataSourceInterface):
    def __init__(self, connection_string):
        self.db = SQLAlchemy(connection_string)
    
    def get_all(self, entity_type):
        return self.db.session.query(entity_type).all()
```

### Additional Services
- **AluguelService**: Rental business logic
- **VendaService**: Sales business logic
- **TransacaoService**: Transaction management

### API Improvements
- **Pagination**: Large dataset handling
- **Filtering**: Advanced query capabilities
- **Caching**: Performance optimization

## Performance Considerations

### Memory Usage
- All data loaded into memory at startup
- Suitable for development and testing
- Consider database for production with large datasets

### Optimization Opportunities
- Lazy loading for large datasets
- Connection pooling for database access
- Caching layer for frequently accessed data

## Security Notes

### Data Validation
- All inputs validated at service layer
- SQL injection prevented through ORM abstraction
- Type safety enforced through interfaces

### Authentication
- Header-based authentication maintained
- Service layer validates user permissions
- Role-based access control ready for implementation

## Conclusion

This refactoring establishes a solid foundation for the RetroHub project with:

- ✅ Clean architecture with proper layer separation
- ✅ Comprehensive test coverage
- ✅ Dependency injection for loose coupling
- ✅ Mock data system for development/testing
- ✅ Business logic encapsulation
- ✅ Error handling and validation
- ✅ Documentation and maintainability

The system is now ready for production development with the ability to easily swap components and extend functionality.
