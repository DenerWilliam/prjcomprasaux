# 🛒 Projeto Compras Aux

Sistema de gerenciamento de listas de compras com integração entre módulos independentes via API REST.

## 📋 Visão Geral

Este projeto consiste em dois módulos independentes que se comunicam via API:

- **`items_app`** - Gerencia produtos disponíveis
- **`basket_app`** - Gerencia carrinhos/listas de compras com referência aos produtos

## 🚀 Instalação

### Pré-requisitos

- Python 3.13+
- pip ou uv (gerenciador de pacotes)

### Passos de Instalação

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd prjcomprasaux
```

2. **Crie um ambiente virtual:**
```bash
python -m venv .venv
```

3. **Ative o ambiente virtual:**
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. **Instale as dependências:**
```bash
pip install -e .
```

5. **Execute as migrações:**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Crie um superusuário (opcional):**
```bash
python manage.py createsuperuser
```

7. **Execute o servidor:**
```bash
python manage.py runserver
```

O projeto estará disponível em `http://localhost:8000`

## 🏗️ Arquitetura

### Módulos

#### `items_app`
- **Modelo:** `Produto`
- **Funcionalidade:** Gerencia produtos disponíveis
- **Campos:** `id`, `nome`, `preco`

#### `basket_app`
- **Modelos:** `Basket`, `BasketItem`
- **Funcionalidade:** Gerencia listas de compras e seus itens
- **Integração:** Busca dados dos produtos via API do `items_app`

### Comunicação entre Módulos

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   basket_app    │ ──────────────► │   items_app     │
│                 │                │                 │
│ Basket          │                │ Produto         │
│ BasketItem      │                │ - id            │
│ - produto_id    │                │ - nome          │
│ - quantidade    │                │ - preco         │
└─────────────────┘                └─────────────────┘
```

## 📚 Documentação da API

### Base URL
```
http://localhost:8000
```

### Endpoints - Produtos (`items_app`)

#### Listar Produtos
```http
GET /api/produtos/
```

**Resposta:**
```json
[
    {
        "id": 1,
        "nome": "Produto A",
        "preco": "29.99"
    }
]
```

#### Criar Produto
```http
POST /api/produtos/
Content-Type: application/json

{
    "nome": "Produto Novo",
    "preco": "19.99"
}
```

#### Buscar Produto Específico
```http
GET /api/produtos/{id}/
```

#### Atualizar Produto
```http
PUT /api/produtos/{id}/
Content-Type: application/json

{
    "nome": "Produto Atualizado",
    "preco": "25.99"
}
```

#### Deletar Produto
```http
DELETE /api/produtos/{id}/
```

### Endpoints - Carrinhos (`basket_app`)

#### Listar Carrinhos
```http
GET /api/baskets/
```

**Resposta:**
```json
[
    {
        "id": 1,
        "nome": "Compras do mês",
        "estabelecimento": "Supermercado ABC",
        "total_itens": 3,
        "valor_total": 89.97,
        "data_criacao": "2024-01-15T10:30:00Z",
        "data_atualizacao": "2024-01-15T10:30:00Z"
    }
]
```

#### Criar Carrinho
```http
POST /api/baskets/
Content-Type: application/json

{
    "nome": "Compras do mês",
    "estabelecimento": "Supermercado ABC"
}
```

#### Buscar Carrinho Específico
```http
GET /api/baskets/{id}/
```

#### Atualizar Carrinho
```http
PUT /api/baskets/{id}/
Content-Type: application/json

{
    "nome": "Lista Atualizada",
    "estabelecimento": "Supermercado XYZ"
}
```

#### Deletar Carrinho
```http
DELETE /api/baskets/{id}/
```

### Endpoints - Itens do Carrinho (`basket_app`)

#### Listar Itens
```http
GET /api/basket-items/
```

**Resposta:**
```json
[
    {
        "id": 1,
        "basket": 1,
        "basket_nome": "Compras do mês - Supermercado ABC",
        "produto_id": 1,
        "produto_nome": "Produto A",
        "produto_preco": "29.99",
        "quantidade": 2,
        "subtotal": 59.98,
        "data_adicionado": "2024-01-15T10:35:00Z"
    }
]
```

#### Adicionar Item ao Carrinho
```http
POST /api/basket-items/
Content-Type: application/json

{
    "basket": 1,
    "produto_id": 1,
    "quantidade": 2
}
```

#### Buscar Item Específico
```http
GET /api/basket-items/{id}/
```

#### Atualizar Item
```http
PUT /api/basket-items/{id}/
Content-Type: application/json

{
    "basket": 1,
    "produto_id": 1,
    "quantidade": 3
}
```

#### Deletar Item
```http
DELETE /api/basket-items/{id}/
```

### Endpoints - Resumos (`basket_app`)

#### Resumo Geral (Todos os Carrinhos)
```http
GET /api/basket-summary/
```

**Resposta:**
```json
{
    "total_itens_unicos": 5,
    "total_quantidade": 12,
    "valor_total": 299.95,
    "itens": [
        {
            "produto_id": 1,
            "produto_nome": "Produto A",
            "quantidade": 2,
            "preco_unitario": 29.99,
            "subtotal": 59.98,
            "basket_id": 1,
            "basket_nome": "Compras do mês - Supermercado ABC"
        }
    ]
}
```

#### Resumo de Carrinho Específico
```http
GET /api/basket-summary/{basket_id}/
```

**Resposta:**
```json
{
    "basket_info": {
        "basket_id": 1,
        "basket_nome": "Compras do mês",
        "estabelecimento": "Supermercado ABC",
        "data_criacao": "2024-01-15T10:30:00Z"
    },
    "total_itens_unicos": 3,
    "total_quantidade": 7,
    "valor_total": 149.95,
    "itens": [
        {
            "produto_id": 1,
            "produto_nome": "Produto A",
            "quantidade": 2,
            "preco_unitario": 29.99,
            "subtotal": 59.98
        }
    ]
}
```

## 🔧 Configuração

### Variáveis de Ambiente

Você pode configurar a URL da API do `items_app` nas settings:

```python
# settings.py
ITEMS_API_URL = 'http://localhost:8000/api/produtos/'
```

### Banco de Dados

O projeto usa SQLite por padrão. Para usar outro banco, configure em `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'seu_banco',
        'USER': 'seu_usuario',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📝 Exemplos de Uso

### Fluxo Completo de Uso

1. **Criar produtos:**
```bash
curl -X POST http://localhost:8000/api/produtos/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Arroz", "preco": "5.99"}'
```

2. **Criar carrinho:**
```bash
curl -X POST http://localhost:8000/api/baskets/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Compras do mês", "estabelecimento": "Supermercado ABC"}'
```

3. **Adicionar itens ao carrinho:**
```bash
curl -X POST http://localhost:8000/api/basket-items/ \
  -H "Content-Type: application/json" \
  -d '{"basket": 1, "produto_id": 1, "quantidade": 2}'
```

4. **Ver resumo do carrinho:**
```bash
curl http://localhost:8000/api/basket-summary/1/
```

### Casos de Uso

#### Lista de Compras para Supermercado
```json
{
    "nome": "Compras do mês",
    "estabelecimento": "Supermercado ABC"
}
```

#### Lista de Compras para Farmácia
```json
{
    "nome": "Medicamentos",
    "estabelecimento": "Farmácia XYZ"
}
```

#### Lista de Compras para Padaria
```json
{
    "nome": "Pães e frios",
    "estabelecimento": "Padaria do João"
}
```

## 🧪 Testes

Para executar os testes:

```bash
python manage.py test
```

## 📊 Admin Interface

Acesse o admin do Django em:
```
http://localhost:8000/admin/
```

## 🚀 Deploy

### Produção

1. Configure as variáveis de ambiente
2. Use um banco de dados robusto (PostgreSQL)
3. Configure servidor web (Nginx + Gunicorn)
4. Configure HTTPS
5. Configure logs e monitoramento

### Docker (Exemplo)

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte, abra uma issue no repositório ou entre em contato através do email.

---

**Desenvolvido com ❤️ usando Django REST Framework**
