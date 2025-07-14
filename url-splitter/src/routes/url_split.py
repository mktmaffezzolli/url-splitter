from flask import Blueprint, request, jsonify, redirect
from src.models.user import db
from src.models.url_split import URLSplit as UrlSplit
import random
import json

url_split_bp = Blueprint('url_split', __name__)

@url_split_bp.route('/splits', methods=['GET'])
def get_splits():
    """Listar todos os splits"""
    try:
        splits = UrlSplit.query.all()
        splits_data = []
        
        for split in splits:
            # Converter JSON strings para objetos Python
            destinations = json.loads(split.destinations) if isinstance(split.destinations, str) else split.destinations
            weights = json.loads(split.weights) if isinstance(split.weights, str) else split.weights
            
            splits_data.append({
                'id': split.id,
                'slug': split.slug,
                'name': split.name,
                'destinations': destinations,
                'weights': weights
            })
        
        return jsonify(splits_data)
    except Exception as e:
        print(f"Erro ao buscar splits: {e}")
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/splits', methods=['POST'])
def create_split():
    """Criar novo split"""
    try:
        data = request.get_json()
        
        # Validações
        if not data.get('slug'):
            return jsonify({'error': 'Slug é obrigatório'}), 400
        
        if not data.get('name'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
            
        if not data.get('destinations') or len(data['destinations']) == 0:
            return jsonify({'error': 'Pelo menos um destino é obrigatório'}), 400
        
        # Verificar se slug já existe
        existing = UrlSplit.query.filter_by(slug=data['slug']).first()
        if existing:
            return jsonify({'error': 'Slug já existe'}), 400
        
        # Criar novo split (APENAS com parâmetros básicos)
        new_split = UrlSplit(
            slug=data['slug'],
            name=data['name'],
            destinations=json.dumps(data['destinations']),
            weights=json.dumps(data.get('weights', [25] * len(data['destinations'])))
        )
        
        db.session.add(new_split)
        db.session.commit()
        
        print(f"✅ Split criado: {data['slug']}")
        
        return jsonify({
            'id': new_split.id,
            'slug': new_split.slug,
            'name': new_split.name,
            'message': 'Split criado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar split: {e}")
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/splits/<int:split_id>', methods=['PUT'])
def update_split(split_id):
    """Editar split existente"""
    try:
        data = request.get_json()
        
        # Buscar split
        split = UrlSplit.query.get(split_id)
        if not split:
            return jsonify({'error': 'Split não encontrado'}), 404
        
        # Validações
        if not data.get('name'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
            
        if not data.get('destinations') or len(data['destinations']) == 0:
            return jsonify({'error': 'Pelo menos um destino é obrigatório'}), 400
        
        # Validar URLs
        for url in data['destinations']:
            if not url.startswith(('http://', 'https://')):
                return jsonify({'error': f'URL inválida: {url}'}), 400
        
        # Validar pesos
        weights = data.get('weights', [])
        if len(weights) != len(data['destinations']):
            # Se não tiver pesos ou quantidade diferente, distribuir igualmente
            weights = [round(100 / len(data['destinations']), 1)] * len(data['destinations'])
        
        # Garantir que soma dos pesos seja 100%
        total_weight = sum(weights)
        if total_weight != 100:
            # Ajustar proporcionalmente
            weights = [round((w / total_weight) * 100, 1) for w in weights]
        
        # Atualizar split
        split.name = data['name']
        split.destinations = json.dumps(data['destinations'])
        split.weights = json.dumps(weights)
        
        db.session.commit()
        
        print(f"✅ Split editado: {split.slug}")
        
        return jsonify({
            'id': split.id,
            'slug': split.slug,
            'name': split.name,
            'destinations': data['destinations'],
            'weights': weights,
            'message': 'Split atualizado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao editar split: {e}")
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/splits/<int:split_id>', methods=['DELETE'])
def delete_split(split_id):
    """Deletar split"""
    try:
        split = UrlSplit.query.get(split_id)
        if not split:
            return jsonify({'error': 'Split não encontrado'}), 404
        
        slug = split.slug
        db.session.delete(split)
        db.session.commit()
        
        print(f"🗑️ Split deletado: {slug}")
        
        return jsonify({'message': 'Split deletado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao deletar split: {e}")
        return jsonify({'error': str(e)}), 500

@url_split_bp.route('/r/<slug>')
def redirect_split(slug):
    """Redirecionamento do split"""
    try:
        split = UrlSplit.query.filter_by(slug=slug).first()
        if not split:
            return "Split não encontrado", 404
        
        # Converter JSON para objetos Python
        destinations = json.loads(split.destinations) if isinstance(split.destinations, str) else split.destinations
        weights = json.loads(split.weights) if isinstance(split.weights, str) else split.weights
        
        if not destinations:
            return "Nenhum destino configurado", 404
        
        # Escolher destino baseado nos pesos
        if len(weights) == len(destinations):
            chosen_url = random.choices(destinations, weights=weights)[0]
        else:
            chosen_url = random.choice(destinations)
        
        print(f"🔗 Redirecionamento: {slug} -> {chosen_url}")
        
        return redirect(chosen_url)
        
    except Exception as e:
        print(f"❌ Erro no redirecionamento: {e}")
        return "Erro interno", 500

@url_split_bp.route('/splits/<int:split_id>/stats', methods=['GET'])
def get_split_stats(split_id):
    """Obter estatísticas do split"""
    try:
        split = UrlSplit.query.get(split_id)
        if not split:
            return jsonify({'error': 'Split não encontrado'}), 404
        
        destinations = json.loads(split.destinations) if isinstance(split.destinations, str) else split.destinations
        weights = json.loads(split.weights) if isinstance(split.weights, str) else split.weights
        
        return jsonify({
            'id': split.id,
            'slug': split.slug,
            'name': split.name,
            'destinations': destinations,
            'weights': weights
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar estatísticas: {e}")
        return jsonify({'error': str(e)}), 500
