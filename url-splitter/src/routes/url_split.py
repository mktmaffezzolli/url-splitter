from flask import Blueprint, request, jsonify, redirect
from src.models.user import db
from src.models.url_split import URLSplit, URLClick
import random
import re

url_split_bp = Blueprint('url_split', __name__)

def generate_slug(name):
    """Gera slug a partir do nome"""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
    slug = re.sub(r'\s+', '-', slug)
    slug = slug.strip('-')
    return slug

@url_split_bp.route('/splits', methods=['POST'])
def create_split():
    """Criar novo split de URL"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        destinations = data.get('destinations', [])
        
        if not name:
            return jsonify({'error': 'Nome é obrigatório'}), 400
        
        if len(destinations) < 2:
            return jsonify({'error': 'Pelo menos 2 destinos são obrigatórios'}), 400
        
        # Gerar slug único
        base_slug = generate_slug(name)
        slug = base_slug
        counter = 1
        while URLSplit.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Criar split
        split = URLSplit(name=name, slug=slug)
        split.set_destinations(destinations)
        
        db.session.add(split)
        db.session.commit()
        
        return jsonify({
            'message': 'Split criado com sucesso',
            'split': split.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/splits/<slug>', methods=['PUT'])
def update_split(slug):
    """Editar split existente"""
    try:
        split = URLSplit.query.filter_by(slug=slug).first()
        if not split:
            return jsonify({'error': 'Split não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualizar nome se fornecido
        if 'name' in data:
            name = data['name'].strip()
            if name:
                split.name = name
        
        # Atualizar destinos se fornecidos
        if 'destinations' in data:
            destinations = data['destinations']
            
            if len(destinations) < 1:
                return jsonify({'error': 'Pelo menos 1 destino é obrigatório'}), 400
            
            # Filtrar destinos com peso > 0
            active_destinations = [dest for dest in destinations if dest.get('weight', 0) > 0]
            
            if len(active_destinations) < 1:
                return jsonify({'error': 'Pelo menos 1 destino deve ter peso maior que 0'}), 400
            
            split.set_destinations(destinations)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Split atualizado com sucesso',
            'split': split.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/splits/<slug>', methods=['GET'])
def get_split(slug):
    """Obter detalhes de um split específico"""
    try:
        split = URLSplit.query.filter_by(slug=slug).first()
        if not split:
            return jsonify({'error': 'Split não encontrado'}), 404
        
        return jsonify({
            'split': split.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/splits', methods=['GET'])
def list_splits():
    """Listar todos os splits com estatísticas detalhadas"""
    try:
        splits = URLSplit.query.order_by(URLSplit.created_at.desc()).all()
        return jsonify({
            'splits': [split.to_dict() for split in splits]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/splits/<slug>', methods=['DELETE'])
def delete_split(slug):
    """Excluir split"""
    try:
        split = URLSplit.query.filter_by(slug=slug).first()
        if not split:
            return jsonify({'error': 'Split não encontrado'}), 404
        
        db.session.delete(split)
        db.session.commit()
        
        return jsonify({'message': 'Split excluído com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/splits/<slug>/toggle', methods=['POST'])
def toggle_split_status(slug):
    """Ativar/desativar split temporariamente"""
    try:
        split = URLSplit.query.filter_by(slug=slug).first()
        if not split:
            return jsonify({'error': 'Split não encontrado'}), 404
        
        # Implementar lógica de ativar/desativar se necessário
        # Por enquanto, apenas retorna sucesso
        
        return jsonify({
            'message': 'Status do split alterado com sucesso',
            'split': split.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/r/<slug>')
def redirect_split(slug):
    """Redirecionar para destino baseado no split"""
    try:
        split = URLSplit.query.filter_by(slug=slug).first()
        if not split:
            return "Split não encontrado", 404
        
        destinations = split.get_destinations()
        if not destinations:
            return "Nenhum destino configurado", 404
        
        # Filtrar apenas destinos ativos (peso > 0)
        active_destinations = [dest for dest in destinations if dest.get('weight', 0) > 0]
        
        if not active_destinations:
            return "Nenhum destino ativo", 404
        
        # Selecionar destino baseado nos pesos
        total_weight = sum(dest['weight'] for dest in active_destinations)
        if total_weight == 0:
            return "Pesos inválidos", 400
        
        random_num = random.uniform(0, total_weight)
        current_weight = 0
        
        selected_destination = None
        for dest in active_destinations:
            current_weight += dest['weight']
            if random_num <= current_weight:
                selected_destination = dest
                break
        
        if not selected_destination:
            selected_destination = active_destinations[-1]
        
        # Registrar clique detalhado
        click = URLClick(
            url_split_id=split.id,
            destination_url=selected_destination['url'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
        # Incrementar contador total
        split.total_clicks += 1
        
        db.session.add(click)
        db.session.commit()
        
        return redirect(selected_destination['url'])
        
    except Exception as e:
        return f"Erro interno: {str(e)}", 500

@url_split_bp.route('/splits/<slug>/stats', methods=['GET'])
def get_split_stats(slug):
    """Obter estatísticas detalhadas de um split"""
    try:
        split = URLSplit.query.filter_by(slug=slug).first()
        if not split:
            return jsonify({'error': 'Split não encontrado'}), 404
        
        # Estatísticas detalhadas
        stats = split.get_click_stats()
        
        # Cliques recentes (últimos 10)
        recent_clicks = URLClick.query.filter_by(url_split_id=split.id)\
            .order_by(URLClick.clicked_at.desc())\
            .limit(10).all()
        
        return jsonify({
            'split': split.to_dict(),
            'detailed_stats': stats,
            'recent_clicks': [click.to_dict() for click in recent_clicks]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/splits/<slug>/redistribute', methods=['POST'])
def redistribute_weights(slug):
    """Redistribuir pesos automaticamente entre destinos ativos"""
    try:
        split = URLSplit.query.filter_by(slug=slug).first()
        if not split:
            return jsonify({'error': 'Split não encontrado'}), 404
        
        destinations = split.get_destinations()
        active_destinations = [dest for dest in destinations if dest.get('weight', 0) > 0]
        
        if len(active_destinations) < 1:
            return jsonify({'error': 'Pelo menos 1 destino deve estar ativo'}), 400
        
        # Redistribuir igualmente entre destinos ativos
        weight_per_destination = 100 // len(active_destinations)
        remainder = 100 % len(active_destinations)
        
        for i, dest in enumerate(destinations):
            if dest.get('weight', 0) > 0:
                dest['weight'] = weight_per_destination
                if i < remainder:  # Distribuir resto nos primeiros destinos
                    dest['weight'] += 1
            else:
                dest['weight'] = 0
        
        split.set_destinations(destinations)
        db.session.commit()
        
        return jsonify({
            'message': 'Pesos redistribuídos com sucesso',
            'split': split.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

