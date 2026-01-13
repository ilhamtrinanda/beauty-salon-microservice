from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_NAME', 'review_db')
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id VARCHAR(255) NOT NULL,
            salon_id INT NOT NULL,
            rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'Review Service is running'})

# Get all reviews
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM reviews ORDER BY created_at DESC')
        reviews = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': reviews})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Get review by ID
@app.route('/api/reviews/<int:id>', methods=['GET'])
def get_review(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM reviews WHERE id = %s', (id,))
        review = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if review:
            return jsonify({'success': True, 'data': review})
        else:
            return jsonify({'success': False, 'message': 'Review not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Get reviews by salon ID
@app.route('/api/reviews/salon/<int:salon_id>', methods=['GET'])
def get_reviews_by_salon(salon_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM reviews WHERE salon_id = %s ORDER BY created_at DESC', (salon_id,))
        reviews = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': reviews})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Create review
@app.route('/api/reviews', methods=['POST'])
def create_review():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reviews (customer_id, salon_id, rating, comment)
            VALUES (%s, %s, %s, %s)
        ''', (data['customer_id'], data['salon_id'], data['rating'], data.get('comment', '')))
        
        conn.commit()
        review_id = cursor.lastrowid
        
        cursor.execute('SELECT * FROM reviews WHERE id = %s', (review_id,))
        review = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': {
            'id': review[0],
            'customer_id': review[1],
            'salon_id': review[2],
            'rating': review[3],
            'comment': review[4],
            'created_at': str(review[5])
        }}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Update review
@app.route('/api/reviews/<int:id>', methods=['PUT'])
def update_review(id):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reviews 
            SET rating = %s, comment = %s
            WHERE id = %s
        ''', (data['rating'], data.get('comment', ''), id))
        
        conn.commit()
        
        cursor.execute('SELECT * FROM reviews WHERE id = %s', (id,))
        review = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if review:
            return jsonify({'success': True, 'data': {
                'id': review[0],
                'customer_id': review[1],
                'salon_id': review[2],
                'rating': review[3],
                'comment': review[4],
                'created_at': str(review[5])
            }})
        else:
            return jsonify({'success': False, 'message': 'Review not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Delete review
@app.route('/api/reviews/<int:id>', methods=['DELETE'])
def delete_review(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM reviews WHERE id = %s', (id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Review deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)