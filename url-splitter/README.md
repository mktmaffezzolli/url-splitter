# URL Splitter - Solução de Split de Tráfego

Uma solução econômica e eficiente para dividir tráfego de campanhas entre múltiplos destinos.

## 🎯 Problema Resolvido

Substitui ferramentas caras como LinkSplit ($588/ano) e Replug ($588/ano) por uma solução própria que custa apenas o valor da hospedagem.

## ✨ Funcionalidades

- **Split de Tráfego**: Distribui visitantes entre múltiplas URLs baseado em pesos
- **Interface Web**: Gerenciamento completo via interface amigável
- **Analytics**: Rastreamento de cliques e estatísticas detalhadas
- **Flexibilidade**: Pesos customizáveis e edição de splits
- **Performance**: Redirecionamentos instantâneos

## 🚀 Início Rápido

### Desenvolvimento Local
```bash
cd url-splitter
source venv/bin/activate
python src/main.py
```

Acesse: http://localhost:5000

### Deploy em Produção
```bash
# Atualizar dependências
pip freeze > requirements.txt

# Deploy (exemplo com Heroku)
git init
git add .
git commit -m "Initial commit"
heroku create seu-app-name
git push heroku main
```

## 📊 Como Usar

1. **Criar Split**: Acesse a interface e crie um novo split
2. **Configurar Destinos**: Adicione URLs e pesos para cada destino
3. **Usar em Campanhas**: Use a URL gerada em suas campanhas
4. **Monitorar**: Acompanhe estatísticas na interface

### Exemplo
```
URL do Split: https://seu-app.com/api/r/atendentes
Destinos:
- https://wa.me/5511999999001 (25%)
- https://wa.me/5511999999002 (25%)
- https://wa.me/5511999999003 (25%)
- https://wa.me/5511999999004 (25%)
```

## 🏗️ Arquitetura

### Backend (Flask)
- **Framework**: Flask com SQLAlchemy
- **Banco**: SQLite (produção pode usar PostgreSQL)
- **API**: RESTful endpoints para CRUD de splits

### Frontend
- **Interface**: HTML/CSS/JavaScript vanilla
- **Design**: Responsivo e moderno
- **UX**: Interface intuitiva para gerenciamento

### Modelos de Dados
```python
UrlSplit:
- id, slug, name
- destinations (JSON)
- weights (JSON)
- total_clicks, created_at

ClickLog:
- url_split_id, destination_url
- ip_address, user_agent
- clicked_at
```

## 🔧 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/splits` | Lista todos os splits |
| POST | `/api/splits` | Cria novo split |
| PUT | `/api/splits/{id}` | Atualiza split |
| DELETE | `/api/splits/{id}` | Remove split |
| GET | `/api/splits/{id}/stats` | Estatísticas do split |
| GET | `/api/r/{slug}` | Redirecionamento |

## 💰 Comparação de Custos

| Solução | Custo Anual | Limitações |
|---------|-------------|------------|
| LinkSplit Pro | $588 | 50k cliques, 20 destinos |
| Replug Professional | $588 | 50k cliques, 5 domínios |
| **Nossa Solução** | **~$60-120** | **Ilimitado** |

## 🔒 Segurança

- Validação de URLs
- Sanitização de entradas
- Prevenção XSS
- Slugs únicos obrigatórios

## 📈 Melhorias Futuras

- [ ] Sistema de autenticação
- [ ] Dashboard com gráficos
- [ ] Filtros geográficos
- [ ] API para integração
- [ ] Agendamento de splits
- [ ] Webhook notifications

## 🛠️ Tecnologias

- **Backend**: Python 3.11, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript ES6
- **Banco**: SQLite (dev), PostgreSQL (prod)
- **Deploy**: Heroku, DigitalOcean, AWS, Vercel

## 📝 Licença

Este projeto foi desenvolvido como solução personalizada. Todos os direitos reservados.

## 🤝 Suporte

Para dúvidas, customizações ou suporte técnico, consulte o GUIA_DE_USO.md ou entre em contato com o desenvolvedor.

