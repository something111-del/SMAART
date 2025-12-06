"""
Celery Worker Application
Processes collected data with NLP enrichment
"""

from celery import Celery
import os
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
app = Celery(
    'smaart_worker',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=1,
)

# Import tasks after app initialization
from backend.services.workers.tasks.nlp_enrichment import enrich_post
from backend.services.workers.tasks.spam_detection import detect_spam
from backend.services.workers.tasks.deduplication import check_duplicate

@app.task(name='process_post')
def process_post(post_data):
    """
    Main task to process a collected post
    
    Args:
        post_data: Dictionary containing post information
        
    Returns:
        Processed post data
    """
    start_time = datetime.utcnow()
    logger.info(f"Processing post: {post_data.get('id', 'unknown')}")
    
    try:
        # Step 1: Check for duplicates
        is_duplicate = check_duplicate.delay(post_data).get()
        if is_duplicate:
            logger.info("Duplicate post detected, skipping")
            return {'status': 'duplicate', 'post_id': post_data.get('id')}
        
        # Step 2: Spam detection
        spam_result = detect_spam.delay(post_data).get()
        post_data['is_spam'] = spam_result['is_spam']
        post_data['spam_confidence'] = spam_result['confidence']
        
        if spam_result['is_spam'] and spam_result['confidence'] > 0.9:
            logger.info("High-confidence spam detected, skipping enrichment")
            return {'status': 'spam', 'post_id': post_data.get('id')}
        
        # Step 3: NLP enrichment
        enriched_data = enrich_post.delay(post_data).get()
        post_data.update(enriched_data)
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        post_data['processing_time_ms'] = int(processing_time)
        
        logger.info(f"Post processed successfully in {processing_time}ms")
        
        return {
            'status': 'success',
            'post_id': post_data.get('id'),
            'data': post_data
        }
        
    except Exception as e:
        logger.error(f"Error processing post: {str(e)}")
        return {
            'status': 'error',
            'post_id': post_data.get('id'),
            'error': str(e)
        }


@app.task(name='batch_process_posts')
def batch_process_posts(posts_data):
    """
    Process multiple posts in batch
    
    Args:
        posts_data: List of post dictionaries
        
    Returns:
        List of processing results
    """
    logger.info(f"Batch processing {len(posts_data)} posts")
    
    results = []
    for post in posts_data:
        result = process_post.delay(post)
        results.append(result)
    
    # Wait for all tasks to complete
    processed_results = [r.get() for r in results]
    
    logger.info(f"Batch processing complete: {len(processed_results)} posts")
    
    return processed_results


@app.task(name='cleanup_old_data')
def cleanup_old_data(days=30):
    """
    Cleanup old data from database
    
    Args:
        days: Number of days to keep
    """
    logger.info(f"Cleaning up data older than {days} days")
    # Implementation would delete old records from database
    return {'status': 'success', 'days': days}


if __name__ == '__main__':
    # Run worker
    app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=2'
    ])
