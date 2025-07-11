# URL Splitter - Guia de Uso Completo

## Visão Geral

O URL Splitter é uma solução personalizada e econômica para dividir o tráfego de uma única URL de campanha entre múltiplas URLs de atendentes. Esta solução substitui ferramentas caras como LinkSplit ($588/ano) e Replug ($588/ano) por uma alternativa que custa apenas o valor da hospedagem.

## Funcionalidades Principais

### ✅ Split de Tráfego Inteligente
- Distribui visitantes entre múltiplas URLs baseado em pesos configuráveis
- Algoritmo de distribuição aleatória ponderada
- Suporte a quantos destinos você precisar

### ✅ Interface Web Amigável
- Criação e gerenciamento de splits via interface web
- Visualização de estatísticas em tempo real
- URLs fáceis de copiar e usar em campanhas

### ✅ Rastreamento e Analytics
- Contador de cliques por destino
- Registro de IP e User-Agent para análise
- Histórico completo de redirecionamentos

### ✅ Flexibilidade Total
- Pesos personalizáveis para cada destino
- Edição de splits existentes
- Ativação/desativação de splits

## Como Usar

### 1. Acessar a Interface
Abra seu navegador e acesse: `http://seu-dominio.com` (ou `http://localhost:5000` para teste local)

### 2. Criar um Novo Split

1. **Nome do Split**: Digite um nome descritivo (ex: "Campanha Atendentes Janeiro")
2. **Slug**: O sistema gera automaticamente baseado no nome, mas você pode editar
   - Exemplo: `atendentes-jan` gerará a URL `/api/r/atendentes-jan`
3. **Destinos e Pesos**:
   - Adicione as URLs dos seus atendentes
   - Configure o peso (porcentagem) para cada um
   - Use "Adicionar Destino" para mais URLs

### 3. Usar o Split em Campanhas

Após criar o split, você receberá uma URL como:
```
http://seu-dominio.com/api/r/seu-slug
```

Use esta URL única em todas suas campanhas (Facebook Ads, Google Ads, etc.). O sistema automaticamente distribuirá o tráfego entre seus atendentes.

### 4. Monitorar Resultados

Na seção "Splits Existentes" você pode:
- Ver total de cliques
- Verificar distribuição por destino
- Copiar a URL do split
- Excluir splits não utilizados

## Exemplo Prático

### Cenário: 4 Atendentes com Distribuição Igual

1. **Nome**: "Atendentes WhatsApp"
2. **Destinos**:
   - `https://wa.me/5511999999001` - 25%
   - `https://wa.me/5511999999002` - 25%
   - `https://wa.me/5511999999003` - 25%
   - `https://wa.me/5511999999004` - 25%

3. **URL Gerada**: `http://seu-dominio.com/api/r/atendentes-whatsapp`

### Resultado
Cada visitante que clicar na URL será direcionado aleatoriamente para um dos 4 atendentes, mantendo a distribuição próxima a 25% para cada um.

## Vantagens da Solução

### 💰 Economia Significativa
- **Soluções do mercado**: $588-1.188/ano
- **Nossa solução**: Apenas custo de hospedagem (~$60-120/ano)
- **Economia**: Até 90% menos custos

### 🚀 Performance
- Redirecionamentos instantâneos
- Banco de dados SQLite para alta velocidade
- Interface responsiva e moderna

### 🔧 Controle Total
- Código-fonte disponível para customizações
- Sem limitações de cliques ou destinos
- Hospedagem própria = seus dados

### 📊 Analytics Detalhado
- Rastreamento completo de cliques
- Dados de IP e User-Agent
- Estatísticas por destino

## Instalação e Configuração

### Requisitos
- Python 3.11+
- Flask e dependências (incluídas)
- Servidor web (para produção)

### Instalação Local (Desenvolvimento)
```bash
cd url-splitter
source venv/bin/activate
python src/main.py
```

### Deploy em Produção
A aplicação está pronta para deploy em qualquer provedor que suporte Flask:
- Heroku
- DigitalOcean
- AWS
- Vercel
- Railway

## Estrutura do Projeto

```
url-splitter/
├── src/
│   ├── main.py              # Aplicação principal
│   ├── models/              # Modelos de dados
│   │   ├── user.py         # Modelo de usuário (padrão)
│   │   └── url_split.py    # Modelo de splits
│   ├── routes/             # Rotas da API
│   │   ├── user.py         # Rotas de usuário (padrão)
│   │   └── url_split.py    # Rotas de splits
│   ├── static/             # Interface web
│   │   └── index.html      # Interface principal
│   └── database/           # Banco de dados SQLite
├── venv/                   # Ambiente virtual Python
└── requirements.txt        # Dependências
```

## API Endpoints

### Criar Split
```http
POST /api/splits
Content-Type: application/json

{
  "name": "Nome do Split",
  "slug": "slug-unico",
  "destinations": ["https://url1.com", "https://url2.com"],
  "weights": [50, 50]
}
```

### Listar Splits
```http
GET /api/splits
```

### Redirecionamento
```http
GET /api/r/{slug}
```

### Estatísticas
```http
GET /api/splits/{id}/stats
```

## Segurança e Boas Práticas

### 🔒 Validações Implementadas
- Validação de URLs válidas
- Slugs únicos obrigatórios
- Sanitização de entradas
- Prevenção de ataques XSS

### 📝 Recomendações
1. Use HTTPS em produção
2. Configure backup regular do banco de dados
3. Monitore logs de acesso
4. Implemente autenticação se necessário

## Suporte e Customizações

### Possíveis Melhorias
- Sistema de autenticação
- Dashboard com gráficos avançados
- API para integração externa
- Filtros por geolocalização
- Agendamento de splits

### Manutenção
- Backup regular do arquivo `src/database/app.db`
- Monitoramento de logs
- Atualizações de segurança

## Conclusão

Esta solução oferece todas as funcionalidades necessárias para split de URL profissional, com economia significativa e controle total. É ideal para empresas que precisam distribuir leads entre múltiplos atendentes de forma eficiente e econômica.

Para dúvidas ou suporte, consulte a documentação técnica ou entre em contato com o desenvolvedor.

