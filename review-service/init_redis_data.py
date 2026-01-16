import redis
import os
import time
from datetime import datetime

def init_redis_data():
    """Initialize Redis with dummy data"""
    
    # Wait for Redis to be ready
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD', None),
                decode_responses=True
            )
            redis_client.ping()
            print("✅ Connected to Redis successfully!")
            break
        except Exception as e:
            retry_count += 1
            print(f"⏳ Waiting for Redis... ({retry_count}/{max_retries})")
            time.sleep(2)
    
    if retry_count >= max_retries:
        print("❌ Failed to connect to Redis")
        return
    
    # Check if data already exists
    if redis_client.exists('review:id:counter'):
        print("ℹ️ Data already exists in Redis, skipping initialization")
        return
    
    # Dummy data
    dummy_reviews = [
        {
            'customer_id': 'CUST001',
            'salon_id': 1,
            'rating': 5,
            'comment': 'Excellent service! Very professional and friendly staff.',
            'created_at': '2024-01-15T10:30:00'
        },
        {
            'customer_id': 'CUST002',
            'salon_id': 1,
            'rating': 4,
            'comment': 'Great haircut, will come back again!',
            'created_at': '2024-01-16T14:20:00'
        },
        {
            'customer_id': 'CUST003',
            'salon_id': 2,
            'rating': 5,
            'comment': 'Best salon in town. Highly recommended!',
            'created_at': '2024-01-17T09:15:00'
        },
        {
            'customer_id': 'CUST004',
            'salon_id': 2,
            'rating': 3,
            'comment': 'Good service but a bit pricey.',
            'created_at': '2024-01-18T16:45:00'
        },
        {
            'customer_id': 'CUST005',
            'salon_id': 1,
            'rating': 5,
            'comment': 'Amazing experience! The stylist really understood what I wanted.',
            'created_at': '2024-01-19T11:00:00'
        },
        {
            'customer_id': 'CUST006',
            'salon_id': 3,
            'rating': 4,
            'comment': 'Very clean and modern salon. Professional service.',
            'created_at': '2024-01-20T13:30:00'
        },
        {
            'customer_id': 'CUST007',
            'salon_id': 3,
            'rating': 5,
            'comment': 'Love my new hairstyle! Thank you!',
            'created_at': '2024-01-21T15:00:00'
        },
        {
            'customer_id': 'CUST008',
            'salon_id': 2,
            'rating': 4,
            'comment': 'Good quality service. Staff is very polite.',
            'created_at': '2024-01-22T10:00:00'
        }
    ]
    
    print(f"📝 Adding {len(dummy_reviews)} dummy reviews to Redis...")
    
    for idx, review in enumerate(dummy_reviews, 1):
        review_id = idx
        review_key = f'review:{review_id}'
        
        # Save review to Redis hash
        review_data = {
            'id': review_id,
            'customer_id': review['customer_id'],
            'salon_id': review['salon_id'],
            'rating': review['rating'],
            'comment': review['comment'],
            'created_at': review['created_at']
        }
        
        redis_client.hset(review_key, mapping=review_data)
        
        # Add review ID to salon's review set
        salon_key = f"salon:{review['salon_id']}:reviews"
        redis_client.sadd(salon_key, review_id)
        
        print(f"  ✓ Added review {review_id}: {review['comment'][:50]}...")
    
    # Set the counter
    redis_client.set('review:id:counter', len(dummy_reviews))
    
    print(f"✅ Successfully initialized {len(dummy_reviews)} reviews in Redis!")
    print(f"📊 Statistics:")
    print(f"   - Total reviews: {len(dummy_reviews)}")
    print(f"   - Salon 1: {sum(1 for r in dummy_reviews if r['salon_id'] == 1)} reviews")
    print(f"   - Salon 2: {sum(1 for r in dummy_reviews if r['salon_id'] == 2)} reviews")
    print(f"   - Salon 3: {sum(1 for r in dummy_reviews if r['salon_id'] == 3)} reviews")

if __name__ == '__main__':
    init_redis_data()