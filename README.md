# 🛒 Projeto Compras Aux

Sistema de gerenciamento de listas de compras com integração entre módulos independentes via API REST.

## 📋 Visão Geral

O projeto é composto por dois módulos principais, cada um com responsabilidade clara e comunicação via API REST:

- **`items_app`**: Gerencia o cadastro e consulta de produtos disponíveis.
- **`basket_app`**: Gerencia listas/carrinhos de compras, referenciando produtos do `items_app` via API.

## 🚀 Instalação

### Pré-requisitos

- Python 3.10+ (recomendado)
- pip (ou uv)
- Git

### Passos de Instalação

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd prjcomprasaux
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python3 -m venv .venv
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
   pip install -r requirements.txt
   ```

5. **Execute as migrações:**
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

6. **Crie um superusuário (opcional):**
   ```bash
   python3 manage.py createsuperuser
   ```

7. **Execute o servidor:**
   ```bash
   python3 manage.py runserver
   ```

O projeto estará disponível em `http://localhost:8000`

## 🏗️ Arquitetura

### Módulos

#### `items_app`
- **Modelo:** `Produto`
- **Campos:** `id`, `nome`, `preco`
- **Responsabilidade:** Cadastro e consulta de produtos.

#### `basket_app`
- **Modelos:** `Basket`, `BasketItem`
- **Responsabilidade:** Gerenciamento de listas/carrinhos de compras e seus itens, integrando produtos via API do `items_app`.

### Comunicação entre Módulos
