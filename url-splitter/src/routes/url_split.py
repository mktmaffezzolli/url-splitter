from flask import Blueprint, request, jsonify, redirect
from src.models.url_split import db, UrlSplit, ClickLog
import random
import re

url_split_bp = Blueprint('url_split', __name__)

def is_valid_url(url):
    """Valida se a URL está em formato correto"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def weighted_random_choice(destinations, weights):
    """Seleciona um destino baseado nos pesos definidos"""
    if len(destinations) != len(weights):
        # Se os pesos não batem, distribui igualmente
        return random.choice(destinations)
    
    # Normaliza os pesos para somar 100
    total_weight = sum(weights)
    if total_weight == 0:
        return random.choice(destinations)
    
    normalized_weights = [w / total_weight for w in weights]
    
    # Seleciona baseado nos pesos
    rand = random.random()
    cumulative = 0
    for i, weight in enumerate(normalized_weights):
        cumulative += weight
        if rand <= cumulative:
            return destinations[i]
    
    # Fallback
    return destinations[-1]

@url_split_bp.route('/splits', methods=['GET'])
def get_splits():
    """Lista todos os splits de URL"""
    splits = UrlSplit.query.filter_by(is_active=True).all()
    return jsonify([split.to_dict() for split in splits])

@url_split_bp.route('/splits', methods=['POST'])
def create_split():
    """Cria um novo split de URL"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400
    
    slug = data.get('slug', '').strip()
    name = data.get('name', '').strip()
    destinations = data.get('destinations', [])
    weights = data.get('weights', [])
    
    # Validações
    if not slug:
        return jsonify({'error': 'Slug é obrigatório'}), 400
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        return jsonify({'error': 'Slug deve conter apenas letras, números, _ e -'}), 400
    
    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    
    if not destinations or len(destinations) < 2:
        return jsonify({'error': 'Pelo menos 2 destinos são necessários'}), 400
    
    # Valida URLs
    for url in destinations:
        if not is_valid_url(url):
            return jsonify({'error': f'URL inválida: {url}'}), 400
    
    # Se pesos não fornecidos, distribui igualmente
    if not weights or len(weights) != len(destinations):
        weights = [100 / len(destinations)] * len(destinations)
    
    # Verifica se slug já existe
    existing = UrlSplit.query.filter_by(slug=slug, is_active=True).first()
    if existing:
        return jsonify({'error': 'Slug já existe'}), 400
    
    try:
        split = UrlSplit(slug=slug, name=name, destinations=destinations, weights=weights)
        db.session.add(split)
        db.session.commit()
        
        return jsonify(split.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar split'}), 500

@url_split_bp.route('/splits/<int:split_id>', methods=['PUT'])
def update_split(split_id):
    """Atualiza um split de URL existente"""
    split = UrlSplit.query.get_or_404(split_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400
    
    name = data.get('name', '').strip()
    destinations = data.get('destinations', [])
    weights = data.get('weights', [])
    
    # Validações
    if name:
        split.name = name
    
    if destinations:
        if len(destinations) < 2:
            return jsonify({'error': 'Pelo menos 2 destinos são necessários'}), 400
        
        # Valida URLs
        for url in destinations:
            if not is_valid_url(url):
                return jsonify({'error': f'URL inválida: {url}'}), 400
        
        split.set_destinations(destinations)
    
    if weights and len(weights) == len(split.get_destinations()):
        split.set_weights(weights)
    
    try:
        db.session.commit()
        return jsonify(split.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar split'}), 500

@url_split_bp.route('/splits/<int:split_id>', methods=['DELETE'])
def delete_split(split_id):
    """Desativa um split de URL"""
    split = UrlSplit.query.get_or_404(split_id)
    split.is_active = False
    
    try:
        db.session.commit()
        return jsonify({'message': 'Split desativado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao desativar split'}), 500

@url_split_bp.route('/splits/<int:split_id>/stats', methods=['GET'])
def get_split_stats(split_id):
    """Obtém estatísticas de um split"""
    split = UrlSplit.query.get_or_404(split_id)
    
    # Conta cliques por destino
    clicks_by_destination = {}
    logs = ClickLog.query.filter_by(url_split_id=split_id).all()
    
    for log in logs:
        if log.destination_url not in clicks_by_destination:
            clicks_by_destination[log.destination_url] = 0
        clicks_by_destination[log.destination_url] += 1
    
    return jsonify({
        'split': split.to_dict(),
        'clicks_by_destination': clicks_by_destination,
        'total_clicks': len(logs)
    })

@url_split_bp.route('/r/<slug>')
def redirect_split(slug):
    """Redireciona para um dos destinos baseado no split configurado"""
    split = UrlSplit.query.filter_by(slug=slug, is_active=True).first()
    
    if not split:
        return jsonify({'error': 'Split não encontrado'}), 404
    
    destinations = split.get_destinations()
    weights = split.get_weights()
    
    if not destinations:
        return jsonify({'error': 'Nenhum destino configurado'}), 404
    
    # Seleciona destino baseado nos pesos
    selected_destination = weighted_random_choice(destinations, weights)
    
    # Registra o clique
    try:
        click_log = ClickLog(
            url_split_id=split.id,
            destination_url=selected_destination,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(click_log)
        
        # Atualiza contador total
        split.total_clicks += 1
        db.session.commit()
    except Exception as e:
        # Se falhar ao registrar, ainda redireciona
        db.session.rollback()
    
    return redirect(selected_destination, code=302)

