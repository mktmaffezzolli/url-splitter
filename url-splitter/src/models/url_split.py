from src.models.user import db
from datetime import datetime
import json

class URLSplit(db.Model):
    __tablename__ = 'url_splits'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    destinations_json = db.Column(db.Text, nullable=False)
    total_clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com cliques
    clicks = db.relationship('URLClick', backref='url_split', lazy=True, cascade='all, delete-orphan')
    
    def set_destinations(self, destinations):
        """Define os destinos do split"""
        self.destinations_json = json.dumps(destinations)
    
    def get_destinations(self):
        """Retorna os destinos do split"""
        try:
            return json.loads(self.destinations_json) if self.destinations_json else []
        except:
            return []
    
    def get_click_stats(self):
        """Retorna estatísticas detalhadas de cliques por URL"""
        destinations = self.get_destinations()
        stats = {}
        
        # Inicializar stats para todas as URLs
        for dest in destinations:
            stats[dest['url']] = {
                'clicks': 0,
                'percentage': 0,
                'weight': dest.get('weight', 0)
            }
        
        # Contar cliques reais
        if self.total_clicks > 0:
            for click in self.clicks:
                if click.destination_url in stats:
                    stats[click.destination_url]['clicks'] += 1
        
        # Calcular porcentagens
        if self.total_clicks > 0:
            for url in stats:
                stats[url]['percentage'] = round((stats[url]['clicks'] / self.total_clicks) * 100, 1)
        
        return stats
    
    def to_dict(self):
        """Converte o split para dicionário com estatísticas"""
        destinations = self.get_destinations()
        click_stats = self.get_click_stats()
        
        # Adicionar estatísticas aos destinos
        for dest in destinations:
            url = dest['url']
            if url in click_stats:
                dest['clicks'] = click_stats[url]['clicks']
                dest['click_percentage'] = click_stats[url]['percentage']
            else:
                dest['clicks'] = 0
                dest['click_percentage'] = 0
        
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'destinations': destinations,
            'total_clicks': self.total_clicks,
            'click_stats': click_stats,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class URLClick(db.Model):
    __tablename__ = 'url_clicks'
    
    id = db.Column(db.Integer, primary_key=True)
    url_split_id = db.Column(db.Integer, db.ForeignKey('url_splits.id'), nullable=False)
    destination_url = db.Column(db.String(500), nullable=False)
    ip_address = db.Column(db.String(45))  # IPv6 pode ter até 45 caracteres
    user_agent = db.Column(db.Text)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Converte o clique para dicionário"""
        return {
            'id': self.id,
            'url_split_id': self.url_split_id,
            'destination_url': self.destination_url,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None
        }

