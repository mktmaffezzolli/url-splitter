from src.models.user import db
from datetime import datetime
import json

class UrlSplit(db.Model):
    __tablename__ = 'url_splits'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    destinations = db.Column(db.Text, nullable=False)  # JSON string
    weights = db.Column(db.Text, nullable=False)  # JSON string
    total_clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, slug, name, destinations, weights):
        self.slug = slug
        self.name = name
        self.destinations = json.dumps(destinations)
        self.weights = json.dumps(weights)
    
    def get_destinations(self):
        return json.loads(self.destinations)
    
    def get_weights(self):
        return json.loads(self.weights)
    
    def set_destinations(self, destinations):
        self.destinations = json.dumps(destinations)
    
    def set_weights(self, weights):
        self.weights = json.dumps(weights)
    
    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'destinations': self.get_destinations(),
            'weights': self.get_weights(),
            'total_clicks': self.total_clicks,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }

class ClickLog(db.Model):
    __tablename__ = 'click_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    url_split_id = db.Column(db.Integer, db.ForeignKey('url_splits.id'), nullable=False)
    destination_url = db.Column(db.String(500), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, url_split_id, destination_url, ip_address=None, user_agent=None):
        self.url_split_id = url_split_id
        self.destination_url = destination_url
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    def to_dict(self):
        return {
            'id': self.id,
            'url_split_id': self.url_split_id,
            'destination_url': self.destination_url,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'clicked_at': self.clicked_at.isoformat()
        }

