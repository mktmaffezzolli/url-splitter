from flask import Blueprint, request, jsonify, redirect
from src.models.user import db
from src.models.url_split import URLSplit, ClickLog
import random
import re

url_split_bp = Blueprint('url_split', __name__)

def generate_slug(name):
    """Gera slug a partir do nome"""
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:50]

@url_split_bp.route('/splits', methods=['GET'])
def get_splits():
    """Lista todos os splits"""
    try:
        splits = URLSplit.query.filter_by(is_active=True).all()
        return jsonify([split.to_dict() for split in splits])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/splits', methods=['POST'])
def create_split():
    """Cria um novo split"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        slug = data.get('slug', '').strip()
        destinations = data.get('destinations', [])
        weights = data.get('weights', [])
        
        if not name:
            return jsonify({'error': 'Nome é obrigatório'}), 400
        
        if not slug:
            slug = generate_slug(name)
        
        if not destinations or len(destinations) < 2:
            return jsonify({'error': 'Pelo menos 2 destinos são necessários'}), 400
        
        if len(destinations) != len(weights):
            return jsonify({'error': 'Número de destinos e pesos deve ser igual'}), 400
        
        # Verificar se slug já existe
        existing = URLSplit.query.filter_by(slug=slug).first()
        if existing:
            return jsonify({'error': 'Slug já existe'}), 400
        
        # Criar split
        split = URLSplit(
            slug=slug,
            name=name,
            destinations=destinations,
            weights=weights
        )
        
        db.session.add(split)
        db.session.commit()
        
        return jsonify(split.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/splits/<int:split_id>', methods=['PUT'])
def update_split(split_id):
    """Atualiza um split existente"""
    try:
        split = URLSplit.query.get_or_404(split_id)
        data = request.get_json()
        
        if 'name' in data:
            split.name = data['name']
        
        if 'destinations' in data:
            split.set_destinations(data['destinations'])
        
        if 'weights' in data:
            split.set_weights(data['weights'])
        
        if 'is_active' in data:
            split.is_active = data['is_active']
        
        db.session.commit()
        return jsonify(split.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/splits/<int:split_id>', methods=['DELETE'])
def delete_split(split_id):
    """Deleta um split"""
    try:
        split = URLSplit.query.get_or_404(split_id)
        split.is_active = False
        db.session.commit()
        return jsonify({'message': 'Split deletado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/r/<slug>')
def redirect_split(slug):
    """Redireciona baseado no split"""
    try:
        split = URLSplit.query.filter_by(slug=slug, is_active=True).first()
        
        if not split:
            return "Split não encontrado", 404
        
        destinations = split.get_destinations()
        weights = split.get_weights()
        
        if not destinations:
            return "Nenhum destino configurado", 404
        
        # Escolher destino baseado nos pesos
        if len(destinations) == 1:
            chosen_url = destinations[0]
        else:
            # Normalizar pesos
            total_weight = sum(weights) if weights else len(destinations)
            if total_weight == 0:
                chosen_url = random.choice(destinations)
            else:
                normalized_weights = [w/total_weight for w in weights] if weights else [1/len(destinations)] * len(destinations)
                chosen_url = random.choices(destinations, weights=normalized_weights)[0]
        
        # Registrar click
        try:
            click_log = ClickLog(
                url_split_id=split.id,
                destination_url=chosen_url,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(click_log)
            
            # Incrementar contador
            split.total_clicks += 1
            db.session.commit()
            
        except Exception as e:
            print(f"Erro ao registrar click: {e}")
            db.session.rollback()
        
        return redirect(chosen_url)
        
    except Exception as e:
        print(f"Erro no redirecionamento: {e}")
        return "Erro interno", 500

@url_split_bp.route('/splits/<int:split_id>/analytics')
def get_analytics(split_id):
    """Retorna analytics de um split"""
    try:
        split = URLSplit.query.get_or_404(split_id)
        
        # Buscar logs de click
        clicks = ClickLog.query.filter_by(url_split_id=split_id).all()
        
        # Contar clicks por destino
        click_counts = {}
        for click in clicks:
            url = click.destination_url
            click_counts[url] = click_counts.get(url, 0) + 1
        
        # Preparar dados
        destinations = split.get_destinations()
        analytics_data = []
        
        for dest in destinations:
            count = click_counts.get(dest, 0)
            percentage = (count / split.total_clicks * 100) if split.total_clicks > 0 else 0
            
            analytics_data.append({
                'url': dest,
                'clicks': count,
                'percentage': round(percentage, 1)
            })
        
        return jsonify({
            'split': split.to_dict(),
            'analytics': analytics_data,
            'total_clicks': split.total_clicks
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

