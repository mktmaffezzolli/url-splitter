# Instruções de Deploy - URL Splitter

## Opções de Deploy

### 1. Heroku (Recomendado para Iniciantes)

#### Pré-requisitos
- Conta no Heroku
- Git instalado
- Heroku CLI instalado

#### Passos
```bash
# 1. Preparar o projeto
cd url-splitter
echo "web: python src/main.py" > Procfile
echo "python-3.11.0" > runtime.txt

# 2. Inicializar Git
git init
git add .
git commit -m "Initial commit"

# 3. Criar app no Heroku
heroku create seu-app-name

# 4. Deploy
git push heroku main

# 5. Abrir aplicação
heroku open
```

**Custo**: Gratuito (com limitações) ou $7/mês

### 2. DigitalOcean App Platform

#### Passos
1. Conecte seu repositório GitHub
2. Configure:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `python src/main.py`
   - **Port**: 5000

**Custo**: $5-12/mês

### 3. Railway

#### Passos
```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login e deploy
railway login
railway init
railway up
```

**Custo**: $5/mês

### 4. Vercel (Serverless)

#### Configuração
Criar arquivo `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "src/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "src/main.py"
    }
  ]
}
```

**Custo**: Gratuito (com limitações)

### 5. AWS EC2 (Avançado)

#### Configuração
```bash
# 1. Conectar ao servidor
ssh -i sua-chave.pem ubuntu@seu-ip

# 2. Instalar dependências
sudo apt update
sudo apt install python3-pip nginx

# 3. Clonar projeto
git clone seu-repositorio
cd url-splitter

# 4. Configurar ambiente
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configurar Nginx
sudo nano /etc/nginx/sites-available/url-splitter
```

Configuração Nginx:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Custo**: $5-20/mês

## Configurações de Produção

### 1. Variáveis de Ambiente
```bash
# Heroku
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=sua-chave-secreta-aqui

# Outros provedores
export FLASK_ENV=production
export SECRET_KEY=sua-chave-secreta-aqui
```

### 2. Banco de Dados
Para produção, considere PostgreSQL:

```python
# src/main.py
import os

if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
```

### 3. HTTPS
- Configure SSL/TLS no seu provedor
- Use certificados Let's Encrypt (gratuitos)
- Redirecione HTTP para HTTPS

### 4. Domínio Personalizado
```bash
# Heroku
heroku domains:add seu-dominio.com

# Configure DNS
# CNAME: seu-dominio.com -> seu-app.herokuapp.com
```

## Monitoramento e Manutenção

### 1. Logs
```bash
# Heroku
heroku logs --tail

# DigitalOcean
doctl apps logs seu-app-id

# AWS
sudo tail -f /var/log/nginx/access.log
```

### 2. Backup do Banco
```bash
# Backup automático (cron job)
0 2 * * * cp /caminho/para/app.db /backup/app_$(date +\%Y\%m\%d).db
```

### 3. Monitoramento
- Configure alertas de uptime
- Monitore uso de recursos
- Acompanhe logs de erro

## Custos Estimados

| Provedor | Custo Mensal | Recursos |
|----------|--------------|----------|
| Heroku Hobby | $7 | 512MB RAM, SSL |
| DigitalOcean | $5 | 512MB RAM, 1 vCPU |
| Railway | $5 | 512MB RAM, 1 vCPU |
| Vercel | Gratuito | Serverless |
| AWS EC2 t2.micro | $5-10 | 1GB RAM, 1 vCPU |

## Checklist de Deploy

- [ ] Código testado localmente
- [ ] Requirements.txt atualizado
- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados configurado
- [ ] SSL/HTTPS habilitado
- [ ] Domínio personalizado (opcional)
- [ ] Monitoramento configurado
- [ ] Backup automático configurado

## Troubleshooting

### Erro: "Application Error"
- Verifique logs do provedor
- Confirme se todas as dependências estão no requirements.txt
- Verifique variáveis de ambiente

### Erro: "Database not found"
- Confirme se o banco SQLite foi criado
- Verifique permissões de escrita
- Para PostgreSQL, confirme string de conexão

### Erro: "Port already in use"
- Use a variável PORT do ambiente
- Configure Flask para usar porta dinâmica:
```python
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

## Suporte

Para problemas específicos de deploy, consulte a documentação do seu provedor ou entre em contato para suporte técnico.

