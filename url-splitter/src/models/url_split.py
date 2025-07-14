from src.models.user import db
from datetime import datetime
import json
import logging

# Configurar logging para monitoramento
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UrlSplit(db.Model):
    __tablename__ = 'url_splits'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    destinations = db.Column(db.Text, nullable=False)  # JSON string
    weights = db.Column(db.Text, nullable=False)  # JSON string
    total_clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Campos adicionais para robustez
    backup_data = db.Column(db.Text)  # Backup completo em JSON
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    version = db.Column(db.Integer, default=1)
    
    def __init__(self, slug, name, destinations, weights):
        self.slug = slug
        self.name = name
        self.destinations = json.dumps(destinations)
        self.weights = json.dumps(weights)
        self.create_backup()
        logger.info(f"✅ Split criado: {slug}")
    
    def get_destinations(self):
        try:
            return json.loads(self.destinations)
        except (json.JSONDecodeError, TypeError):
            logger.error(f"❌ Erro ao decodificar destinations para split {self.slug}")
            return []
    
    def get_weights(self):
        try:
            return json.loads(self.weights)
        except (json.JSONDecodeError, TypeError):
            logger.error(f"❌ Erro ao decodificar weights para split {self.slug}")
            return []
    
    def set_destinations(self, destinations):
        self.destinations = json.dumps(destinations)
        self.updated_at = datetime.utcnow()
        self.version += 1
        self.create_backup()
        logger.info(f"🔄 Destinations atualizados para split {self.slug}")
    
    def set_weights(self, weights):
        self.weights = json.dumps(weights)
        self.updated_at = datetime.utcnow()
        self.version += 1
        self.create_backup()
        logger.info(f"🔄 Weights atualizados para split {self.slug}")
    
    def create_backup(self):
        """Cria backup completo dos dados do split"""
        backup_data = {
            'slug': self.slug,
            'name': self.name,
            'destinations': self.get_destinations(),
            'weights': self.get_weights(),
            'total_clicks': self.total_clicks,
            'is_active': self.is_active,
            'version': self.version,
            'backup_created_at': datetime.utcnow().isoformat()
        }
        self.backup_data = json.dumps(backup_data)
    
    def restore_from_backup(self):
        """Restaura dados do backup em caso de corrupção"""
        try:
            if self.backup_data:
                backup = json.loads(self.backup_data)
                self.name = backup.get('name', self.name)
                self.destinations = json.dumps(backup.get('destinations', []))
                self.weights = json.dumps(backup.get('weights', []))
                self.total_clicks = backup.get('total_clicks', 0)
                self.is_active = backup.get('is_active', True)
                logger.info(f"🔄 Backup restaurado para split {self.slug}")
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao restaurar backup para split {self.slug}: {e}")
        return False
    
    def update_last_accessed(self):
        """Atualiza timestamp de último acesso"""
        self.last_accessed = datetime.utcnow()
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar last_accessed para split {self.slug}: {e}")
            db.session.rollback()
    
    def increment_clicks(self):
        """Incrementa contador de cliques de forma segura"""
        try:
            self.total_clicks += 1
            self.last_accessed = datetime.utcnow()
            db.session.commit()
            logger.info(f"📊 Click registrado para split {self.slug} (total: {self.total_clicks})")
        except Exception as e:
            logger.error(f"❌ Erro ao incrementar clicks para split {self.slug}: {e}")
            db.session.rollback()
    
    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'destinations': self.get_destinations(),
            'weights': self.get_weights(),
            'total_clicks': self.total_clicks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'is_active': self.is_active,
            'version': self.version
        }
    
    @classmethod
    def get_by_slug_safe(cls, slug):
        """Busca split por slug com tratamento de erro"""
        try:
            split = cls.query.filter_by(slug=slug, is_active=True).first()
            if split:
                split.update_last_accessed()
                logger.info(f"🔍 Split encontrado: {slug}")
            else:
                logger.warning(f"⚠️ Split não encontrado: {slug}")
            return split
        except Exception as e:
            logger.error(f"❌ Erro ao buscar split {slug}: {e}")
            return None
    
    @classmethod
    def create_safe(cls, slug, name, destinations, weights):
        """Cria split com tratamento de erro"""
        try:
            split = cls(slug=slug, name=name, destinations=destinations, weights=weights)
            db.session.add(split)
            db.session.commit()
            logger.info(f"✅ Split criado com sucesso: {slug}")
            return split
        except Exception as e:
            logger.error(f"❌ Erro ao criar split {slug}: {e}")
            db.session.rollback()
            return None

class ClickLog(db.Model):
    __tablename__ = 'click_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    url_split_id = db.Column(db.Integer, db.ForeignKey('url_splits.id'), nullable=False, index=True)
    destination_url = db.Column(db.String(500), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Campos adicionais para analytics
    referrer = db.Column(db.String(500))
    country = db.Column(db.String(2))
    device_type = db.Column(db.String(50))
    
    def __init__(self, url_split_id, destination_url, ip_address=None, user_agent=None, referrer=None):
        self.url_split_id = url_split_id
        self.destination_url = destination_url
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.referrer = referrer
    
    def to_dict(self):
        return {
            'id': self.id,
            'url_split_id': self.url_split_id,
            'destination_url': self.destination_url,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referrer': self.referrer,
            'country': self.country,
            'device_type': self.device_type,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None
        }
    
    @classmethod
    def create_safe(cls, url_split_id, destination_url, ip_address=None, user_agent=None, referrer=None):
        """Cria log de click com tratamento de erro"""
        try:
            click_log = cls(
                url_split_id=url_split_id,
                destination_url=destination_url,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer
            )
            db.session.add(click_log)
            db.session.commit()
            logger.info(f"📊 Click log criado para split_id {url_split_id}")
            return click_log
        except Exception as e:
            logger.error(f"❌ Erro ao criar click log: {e}")
            db.session.rollback()
            return None
