# Guia de Deploy - Projeto prjcomprasaux

Este documento explica como configurar e usar o sistema de CI/CD para deploy automático do projeto Django.

## 📋 Arquivos Criados

- `.github/workflows/deploy.yml` - Workflow do GitHub Actions
- `deploy.sh` - Script de deploy para VM
- `requirements.txt` - Dependências Python
- `env.example` - Exemplo de variáveis de ambiente
- `Dockerfile` - Containerização da aplicação
- `docker-compose.yml` - Orquestração de containers
- `nginx.conf` - Configuração do Nginx

## 🚀 Configuração do GitHub Actions

### 1. Configurar Secrets no GitHub

No seu repositório GitHub, vá em **Settings > Secrets and variables > Actions** e adicione:

- `VM_HOST` - IP ou domínio da sua VM
- `VM_USERNAME` - Usuário SSH da VM
- `VM_SSH_KEY` - Chave privada SSH para acesso à VM
- `VM_PORT` - Porta SSH (padrão: 22)

### 2. Configurar SSH na VM

```bash
# Na VM, criar usuário para deploy
sudo adduser deploy
sudo usermod -aG sudo deploy

# Configurar chave SSH
mkdir -p /home/deploy/.ssh
echo "sua-chave-publica-aqui" >> /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys
chmod 700 /home/deploy/.ssh
chown -R deploy:deploy /home/deploy/.ssh
```

## 🖥️ Configuração da VM

### 1. Instalar dependências

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git nginx postgresql postgresql-contrib

# CentOS/RHEL
sudo yum update
sudo yum install python3 python3-pip git nginx postgresql postgresql-server
```

### 2. Configurar PostgreSQL

```bash
sudo -u postgres createuser --interactive
sudo -u postgres createdb prjcomprasaux_db
```

### 3. Clonar o repositório

```bash
cd /home/deploy
git clone https://github.com/seu-usuario/prjcomprasaux.git
cd prjcomprasaux
```

### 4. Configurar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Configurar variáveis de ambiente

```bash
cp env.example .env
nano .env  # Editar com suas configurações
```

### 6. Configurar Gunicorn

Criar arquivo `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon
After=network.target

[Service]
User=deploy
Group=www-data
WorkingDirectory=/home/deploy/prjcomprasaux
Environment="PATH=/home/deploy/prjcomprasaux/venv/bin"
ExecStart=/home/deploy/prjcomprasaux/venv/bin/gunicorn --workers 3 --bind unix:/home/deploy/prjcomprasaux/prjcomprasaux.sock comprasaux.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 7. Configurar Nginx

Criar arquivo `/etc/nginx/sites-available/prjcomprasaux`:

```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/deploy/prjcomprasaux;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/deploy/prjcomprasaux/prjcomprasaux.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/prjcomprasaux /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 🐳 Deploy com Docker (Alternativo)

### 1. Instalar Docker e Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Configurar variáveis de ambiente

```bash
cp env.example .env
# Editar .env com suas configurações
```

### 3. Executar deploy

```bash
docker-compose up -d
```

## 🔄 Como Funciona o Deploy Automático

1. **Push para main/master**: Quando você faz push para a branch principal
2. **GitHub Actions**: Executa testes e validações
3. **Deploy**: Se os testes passarem, conecta na VM via SSH
4. **Atualização**: Puxa as mudanças do Git, instala dependências, executa migrações
5. **Reinicialização**: Reinicia os serviços Gunicorn e Nginx

## 🛠️ Comandos Úteis

### Deploy manual
```bash
./deploy.sh
```

### Verificar status dos serviços
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
```

### Ver logs
```bash
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log
```

### Backup do banco
```bash
pg_dump prjcomprasaux_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 🔒 Segurança

- Use HTTPS em produção
- Configure firewall adequadamente
- Mantenha dependências atualizadas
- Use variáveis de ambiente para dados sensíveis
- Configure backup automático do banco de dados

## 📞 Suporte

Em caso de problemas:
1. Verifique os logs dos serviços
2. Confirme se todas as dependências estão instaladas
3. Verifique as configurações de rede e firewall
4. Consulte a documentação do Django para troubleshooting
