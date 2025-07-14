from flask import Blueprint, request, jsonify, redirect
from src.models.user import db
from src.models.url_split import URLSplit as UrlSplit
import random
import json

url_split_bp = Blueprint('url_split', __name__)

def safe_json_parse(data, field_name="campo"):
    """
    Função para fazer parse seguro de JSON, tratando casos de JSON duplo
    """
    try:
        if data is None:
            print(f"⚠️ {field_name} é None")
            return []
        
        if isinstance(data, list):
            print(f"✅ {field_name} já é lista: {data}")
            return data
        
        if isinstance(data, str):
            print(f"🔍 {field_name} é string, fazendo parse: {data[:100]}...")
            parsed = json.loads(data)
            
            # Se o resultado ainda for string, fazer parse novamente (JSON duplo)
            if isinstance(parsed, str):
                print(f"🔄 {field_name} é JSON duplo, fazendo segundo parse")
                parsed = json.loads(parsed)
            
            if isinstance(parsed, list):
                print(f"✅ {field_name} parseado com sucesso: {len(parsed)} itens")
                return parsed
            else:
                print(f"❌ {field_name} não é lista após parse: {type(parsed)}")
                return []
        
        print(f"❌ {field_name} tipo não suportado: {type(data)}")
        return []
        
    except json.JSONDecodeError as e:
        print(f"❌ Erro JSON em {field_name}: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro geral em {field_name}: {e}")
        return []

@url_split_bp.route('/splits', methods=['GET'])
def get_splits():
    """Listar todos os splits"""
    try:
        splits = UrlSplit.query.all()
        splits_data = []
        
        print(f"🔍 Encontrados {len(splits)} splits no banco")
        
        for split in splits:
            # Parse seguro dos dados JSON
            destinations = safe_json_parse(split.destinations, "destinations")
            weights = safe_json_parse(split.weights, "weights")
            
            splits_data.append({
                'id': split.id,
                'slug': split.slug,
                'name': split.name,
                'destinations': destinations,
                'weights': weights
            })
        
        return jsonify(splits_data)
    except Exception as e:
        print(f"❌ Erro ao buscar splits: {e}")
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
        
        # Garantir que destinations é uma lista
        destinations = data['destinations']
        if isinstance(destinations, str):
            destinations = [destinations]
        
        # Garantir que weights é uma lista
        weights = data.get('weights', [])
        if not weights or len(weights) != len(destinations):
            weights = [round(100 / len(destinations), 1)] * len(destinations)
        
        print(f"📝 Criando split:")
        print(f"   Slug: {data['slug']}")
        print(f"   Destinations: {destinations}")
        print(f"   Weights: {weights}")
        
        # Criar novo split (APENAS com parâmetros básicos)
        new_split = UrlSplit(
            slug=data['slug'],
            name=data['name'],
            destinations=json.dumps(destinations),  # Garantir que é JSON válido
            weights=json.dumps(weights)  # Garantir que é JSON válido
        )
        
        db.session.add(new_split)
        db.session.commit()
        
        print(f"✅ Split criado: {data['slug']} (ID: {new_split.id})")
        
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
    """Redirecionamento do split - VERSÃO CORRIGIDA PARA JSON"""
    try:
        print(f"🔍 Buscando split com slug: '{slug}'")
        
        # Buscar split no banco de dados
        split = UrlSplit.query.filter_by(slug=slug).first()
        
        if not split:
            print(f"❌ Split '{slug}' não encontrado no banco")
            # Listar todos os splits para debug
            all_splits = UrlSplit.query.all()
            print(f"📋 Splits disponíveis: {[s.slug for s in all_splits]}")
            return jsonify({'error': 'Split not found'}), 404
        
        print(f"✅ Split encontrado: {split.slug} (ID: {split.id})")
        print(f"📊 Dados brutos do banco:")
        print(f"   destinations: {split.destinations}")
        print(f"   weights: {split.weights}")
        
        # Parse seguro dos dados JSON
        destinations = safe_json_parse(split.destinations, "destinations")
        weights = safe_json_parse(split.weights, "weights")
        
        print(f"📍 Destinos parseados: {destinations}")
        print(f"⚖️ Pesos parseados: {weights}")
        
        if not destinations or len(destinations) == 0:
            print("❌ Nenhum destino válido encontrado")
            return jsonify({'error': 'Nenhum destino configurado'}), 404
        
        # Validar que destinations é realmente uma lista de URLs
        valid_destinations = []
        for dest in destinations:
            if isinstance(dest, str) and (dest.startswith('http://') or dest.startswith('https://')):
                valid_destinations.append(dest)
            else:
                print(f"⚠️ Destino inválido ignorado: {dest}")
        
        if not valid_destinations:
            print("❌ Nenhum destino válido após validação")
            return jsonify({'error': 'Nenhum destino válido'}), 404
        
        print(f"✅ Destinos válidos: {valid_destinations}")
        
        # Escolher destino baseado nos pesos
        try:
            if (len(weights) == len(valid_destinations) and 
                all(isinstance(w, (int, float)) and w > 0 for w in weights)):
                chosen_url = random.choices(valid_destinations, weights=weights)[0]
                print(f"🎯 URL escolhida com peso: {chosen_url}")
            else:
                chosen_url = random.choice(valid_destinations)
                print(f"🎯 URL escolhida aleatoriamente: {chosen_url}")
        except Exception as e:
            print(f"❌ Erro ao escolher URL: {e}")
            chosen_url = valid_destinations[0]  # Fallback para primeira URL
            print(f"🔄 Fallback para primeira URL: {chosen_url}")
        
        print(f"🔗 Redirecionando {slug} -> {chosen_url}")
        
        # Fazer redirecionamento
        return redirect(chosen_url, code=302)
        
    except Exception as e:
        print(f"❌ Erro crítico no redirecionamento: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@url_split_bp.route('/splits/<int:split_id>/stats', methods=['GET'])
def get_split_stats(split_id):
    """Obter estatísticas do split"""
    try:
        split = UrlSplit.query.get(split_id)
        if not split:
            return jsonify({'error': 'Split não encontrado'}), 404
        
        destinations = safe_json_parse(split.destinations, "destinations")
        weights = safe_json_parse(split.weights, "weights")
        
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

# Endpoint de debug para verificar splits
@url_split_bp.route('/debug/splits', methods=['GET'])
def debug_splits():
    """Endpoint de debug para verificar splits no banco"""
    try:
        splits = UrlSplit.query.all()
        debug_data = []
        
        for split in splits:
            destinations_raw = split.destinations
            weights_raw = split.weights
            
            destinations_parsed = safe_json_parse(destinations_raw, f"destinations-{split.slug}")
            weights_parsed = safe_json_parse(weights_raw, f"weights-{split.slug}")
            
            debug_data.append({
                'id': split.id,
                'slug': split.slug,
                'name': split.name,
                'destinations_raw': destinations_raw,
                'weights_raw': weights_raw,
                'destinations_parsed': destinations_parsed,
                'weights_parsed': weights_parsed,
                'destinations_type': str(type(destinations_raw)),
                'weights_type': str(type(weights_raw)),
                'destinations_valid': all(isinstance(d, str) and d.startswith(('http://', 'https://')) for d in destinations_parsed),
                'weights_valid': all(isinstance(w, (int, float)) for w in weights_parsed)
            })
        
        return jsonify({
            'total_splits': len(splits),
            'splits': debug_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

