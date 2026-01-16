from flask import Flask, request, jsonify
from flask_cors import CORS
import redis
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Redis configuration
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD', None),
    decode_responses=True
)

def get_next_id():
    """Generate next ID for review"""
    return redis_client.incr('review:id:counter')

def get_review_key(review_id):
    """Generate Redis key for review"""
    return f'review:{review_id}'

def get_salon_reviews_key(salon_id):
    """Generate Redis key for salon reviews set"""
    return f'salon:{salon_id}:reviews'

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    try:
        redis_client.ping()
        return jsonify({'status': 'Review Service is running', 'redis': 'connected'})
    except:
        return jsonify({'status': 'Review Service is running', 'redis': 'disconnected'}), 500

# Get all reviews
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    try:
        # Get all review keys
        keys = redis_client.keys('review:[0-9]*')
        reviews = []
        
        for key in keys:
            # Skip counter key
            if key == 'review:id:counter':
                continue
                
            review_data = redis_client.hgetall(key)
            if review_data:
                reviews.append({
                    'id': int(review_data['id']),
                    'customer_id': review_data['customer_id'],
                    'salon_id': int(review_data['salon_id']),
                    'rating': int(review_data['rating']),
                    'comment': review_data.get('comment', ''),
                    'created_at': review_data['created_at']
                })
        
        # Sort by created_at descending
        reviews.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({'success': True, 'data': reviews})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Get review by ID
@app.route('/api/reviews/<int:id>', methods=['GET'])
def get_review(id):
    try:
        review_key = get_review_key(id)
        review_data = redis_client.hgetall(review_key)
        
        if review_data:
            review = {
                'id': int(review_data['id']),
                'customer_id': review_data['customer_id'],
                'salon_id': int(review_data['salon_id']),
                'rating': int(review_data['rating']),
                'comment': review_data.get('comment', ''),
                'created_at': review_data['created_at']
            }
            return jsonify({'success': True, 'data': review})
        else:
            return jsonify({'success': False, 'message': 'Review not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Get reviews by salon ID
@app.route('/api/reviews/salon/<int:salon_id>', methods=['GET'])
def get_reviews_by_salon(salon_id):
    try:
        salon_key = get_salon_reviews_key(salon_id)
        review_ids = redis_client.smembers(salon_key)
        
        reviews = []
        for review_id in review_ids:
            review_key = get_review_key(review_id)
            review_data = redis_client.hgetall(review_key)
            
            if review_data:
                reviews.append({
                    'id': int(review_data['id']),
                    'customer_id': review_data['customer_id'],
                    'salon_id': int(review_data['salon_id']),
                    'rating': int(review_data['rating']),
                    'comment': review_data.get('comment', ''),
                    'created_at': review_data['created_at']
                })
        
        # Sort by created_at descending
        reviews.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({'success': True, 'data': reviews})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Create review
@app.route('/api/reviews', methods=['POST'])
def create_review():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['customer_id', 'salon_id', 'rating']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Validate rating
        if not (1 <= data['rating'] <= 5):
            return jsonify({'success': False, 'error': 'Rating must be between 1 and 5'}), 400
        
        # Generate new ID
        review_id = get_next_id()
        review_key = get_review_key(review_id)
        
        # Create timestamp
        created_at = datetime.now().isoformat()
        
        # Save review to Redis hash
        review_data = {
            'id': review_id,
            'customer_id': data['customer_id'],
            'salon_id': data['salon_id'],
            'rating': data['rating'],
            'comment': data.get('comment', ''),
            'created_at': created_at
        }
        
        redis_client.hset(review_key, mapping=review_data)
        
        # Add review ID to salon's review set
        salon_key = get_salon_reviews_key(data['salon_id'])
        redis_client.sadd(salon_key, review_id)
        
        return jsonify({'success': True, 'data': {
            'id': review_id,
            'customer_id': review_data['customer_id'],
            'salon_id': int(review_data['salon_id']),
            'rating': int(review_data['rating']),
            'comment': review_data['comment'],
            'created_at': review_data['created_at']
        }}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Update review
@app.route('/api/reviews/<int:id>', methods=['PUT'])
def update_review(id):
    try:
        data = request.get_json()
        review_key = get_review_key(id)
        
        # Check if review exists
        if not redis_client.exists(review_key):
            return jsonify({'success': False, 'message': 'Review not found'}), 404
        
        # Validate rating if provided
        if 'rating' in data and not (1 <= data['rating'] <= 5):
            return jsonify({'success': False, 'error': 'Rating must be between 1 and 5'}), 400
        
        # Update only rating and comment
        update_data = {}
        if 'rating' in data:
            update_data['rating'] = data['rating']
        if 'comment' in data:
            update_data['comment'] = data['comment']
        
        if update_data:
            redis_client.hset(review_key, mapping=update_data)
        
        # Get updated review
        review_data = redis_client.hgetall(review_key)
        
        return jsonify({'success': True, 'data': {
            'id': int(review_data['id']),
            'customer_id': review_data['customer_id'],
            'salon_id': int(review_data['salon_id']),
            'rating': int(review_data['rating']),
            'comment': review_data.get('comment', ''),
            'created_at': review_data['created_at']
        }})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Delete review
@app.route('/api/reviews/<int:id>', methods=['DELETE'])
def delete_review(id):
    try:
        review_key = get_review_key(id)
        
        # Get review data before deleting to remove from salon set
        review_data = redis_client.hgetall(review_key)
        
        if not review_data:
            return jsonify({'success': False, 'message': 'Review not found'}), 404
        
        # Remove from salon's review set
        salon_key = get_salon_reviews_key(review_data['salon_id'])
        redis_client.srem(salon_key, id)
        
        # Delete review
        redis_client.delete(review_key)
        
        return jsonify({'success': True, 'message': 'Review deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize dummy data if needed
    try:
        from init_redis_data import init_redis_data
        init_redis_data()
    except Exception as e:
        print(f"Warning: Could not initialize Redis data: {e}")
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)