import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.url_split import url_split_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configurar CORS para permitir acesso de qualquer origem
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(url_split_bp, url_prefix='/api')

# Configuração ROBUSTA do PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Heroku PostgreSQL - PERSISTENTE PARA SEMPRE
    print("🐘 Conectando ao PostgreSQL...")
    
    # Corrigir URL do Heroku se necessário
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10
        }
    }
    print(f"✅ PostgreSQL configurado: {DATABASE_URL[:50]}...")
else:
    # Fallback para desenvolvimento local
    print("📁 PostgreSQL não encontrado, usando SQLite local...")
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Inicialização ROBUSTA do banco
with app.app_context():
    try:
        # Testar conexão
        db.engine.execute('SELECT 1')
        print("✅ Conexão com banco testada!")
        
        # Criar tabelas
        db.create_all()
        print("✅ Tabelas criadas/verificadas!")
        
        # Verificar se tabelas existem
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✅ Tabelas disponíveis: {tables}")
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        # Tentar novamente com configuração mais simples
        try:
            db.create_all()
            print("✅ Segundo tentativa bem-sucedida!")
        except Exception as e2:
            print(f"❌ Erro crítico: {e2}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/health')
def health_check():
    """Endpoint para verificar saúde da aplicação"""
    try:
        # Testar banco
        db.engine.execute('SELECT 1')
        return {'status': 'ok', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'error', 'database': str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando aplicação na porta {port}")
    print(f"💾 Banco: {'PostgreSQL (PERSISTENTE)' if DATABASE_URL else 'SQLite (Local)'}")
    app.run(host='0.0.0.0', port=port, debug=False)

