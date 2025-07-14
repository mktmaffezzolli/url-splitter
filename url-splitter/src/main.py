import os
import sys
import shutil
import json
from datetime import datetime
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

# Configuração PERSISTENTE do SQLite
def setup_persistent_database():
    """Configura banco SQLite com backup automático"""
    
    # Diretório para dados persistentes
    data_dir = '/app/data'
    backup_dir = '/app/backups'
    
    # Criar diretórios se não existirem
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)
    
    # Caminho do banco principal
    db_path = os.path.join(data_dir, 'url_splitter.db')
    
    print(f"📁 Banco de dados: {db_path}")
    
    return db_path

def backup_database(db_path):
    """Faz backup do banco de dados"""
    try:
        if os.path.exists(db_path):
            backup_dir = '/app/backups'
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'backup_{timestamp}.db')
            
            shutil.copy2(db_path, backup_path)
            print(f"✅ Backup criado: {backup_path}")
            
            # Manter apenas os 5 backups mais recentes
            backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('backup_')])
            if len(backups) > 5:
                for old_backup in backups[:-5]:
                    os.remove(os.path.join(backup_dir, old_backup))
                    print(f"🗑️ Backup antigo removido: {old_backup}")
                    
    except Exception as e:
        print(f"⚠️ Erro no backup: {e}")

# Configurar banco de dados
db_path = setup_persistent_database()
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("🗄️ Usando SQLite PERSISTENTE")

db.init_app(app)

with app.app_context():
    try:
        # Fazer backup antes de qualquer operação
        backup_database(db_path)
        
        # Criar tabelas
        db.create_all()
        print("✅ Banco de dados inicializado!")
        
        # Verificar se há dados
        from src.models.url_split import UrlSplit
        count = UrlSplit.query.count()
        print(f"📊 Splits existentes: {count}")
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")

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

@app.route('/api/backup')
def manual_backup():
    """Endpoint para backup manual"""
    try:
        backup_database(db_path)
        return {'status': 'success', 'message': 'Backup criado com sucesso'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/api/health')
def health_check():
    """Endpoint para verificar saúde da aplicação"""
    try:
        from src.models.url_split import UrlSplit
        count = UrlSplit.query.count()
        return {
            'status': 'ok', 
            'database': 'connected',
            'splits_count': count,
            'database_path': db_path
        }, 200
    except Exception as e:
        return {'status': 'error', 'database': str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando aplicação na porta {port}")
    print(f"💾 SQLite Persistente: {db_path}")
    app.run(host='0.0.0.0', port=port, debug=False)
