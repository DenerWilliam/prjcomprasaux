#!/bin/bash

# Script de Deploy para VM usando uv (https://github.com/astral-sh/uv)
# Este script deve ser executado na VM para fazer o deploy do projeto Django

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy do projeto prjcomprasaux com uv..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    error "manage.py não encontrado. Execute este script no diretório raiz do projeto."
fi

# Verificar se o uv está instalado, se não estiver, instalar automaticamente
if ! command -v uv &> /dev/null; then
    warning "uv não encontrado. Instalando uv com pip..."
    pip install uv || error "Falha ao instalar o uv. Instale manualmente: https://github.com/astral-sh/uv"
fi

# Instalar dependências com uv
log "Instalando/atualizando dependências com uv..."
uv sync

# Executar migrações
log "Executando migrações do banco de dados..."
uv run manage.py migrate

# Coletar arquivos estáticos
log "Coletando arquivos estáticos..."
uv run manage.py collectstatic --noinput

# Executar testes
log "Executando testes..."
uv run manage.py test

# Verificar configurações de produção
log "Verificando configurações de produção..."
uv run manage.py check --deploy

# Reiniciar serviços (se estiver usando systemd)
if systemctl is-active --quiet gunicorn; then
    log "Reiniciando serviço Gunicorn..."
    sudo systemctl restart gunicorn
fi

if systemctl is-active --quiet nginx; then
    log "Reiniciando serviço Nginx..."
    sudo systemctl restart nginx
fi

log "✅ Deploy concluído com sucesso!"

# Mostrar status dos serviços
echo ""
log "Status dos serviços:"
if systemctl is-active --quiet gunicorn; then
    echo -e "${GREEN}✓ Gunicorn: Ativo${NC}"
else
    echo -e "${RED}✗ Gunicorn: Inativo${NC}"
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx: Ativo${NC}"
else
    echo -e "${RED}✗ Nginx: Inativo${NC}"
fi

echo ""
log "🎉 Aplicação disponível em: http://$(curl -s ifconfig.me)"
