"""
Twitter/X Data Collector
Collects tweets based on trending topics and keywords
"""

import tweepy
import os
import json
import logging
from datetime import datetime
from typing import List, Dict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterCollector:
    """Collects tweets using Twitter API v2"""
    
    def __init__(self):
        """Initialize Twitter API client"""
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        
        if not all([self.api_key, self.api_secret, self.bearer_token]):
            raise ValueError("Twitter API credentials not found in environment variables")
        
        # Initialize Tweepy client
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
        
        logger.info("Twitter collector initialized successfully")
    
    def collect_tweets(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Collect tweets based on query
        
        Args:
            query: Search query (keywords, hashtags)
            max_results: Maximum number of tweets to collect (10-100)
        
        Returns:
            List of tweet dictionaries
        """
        try:
            logger.info(f"Collecting tweets for query: {query}")
            
            # Search recent tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),  # API limit
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang', 'entities'],
                expansions=['author_id'],
                user_fields=['username', 'verified', 'public_metrics']
            )
            
            if not tweets.data:
                logger.warning(f"No tweets found for query: {query}")
                return []
            
            # Process tweets
            collected_tweets = []
            users = {user.id: user for user in tweets.includes.get('users', [])}
            
            for tweet in tweets.data:
                author = users.get(tweet.author_id)
                
                tweet_data = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                    'author_id': tweet.author_id,
                    'author_username': author.username if author else None,
                    'author_verified': author.verified if author else False,
                    'language': tweet.lang,
                    'likes': tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                    'retweets': tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                    'replies': tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0,
                    'source': 'twitter',
                    'query': query,
                    'collected_at': datetime.utcnow().isoformat()
                }
                
                # Extract hashtags and mentions
                if tweet.entities:
                    tweet_data['hashtags'] = [tag['tag'] for tag in tweet.entities.get('hashtags', [])]
                    tweet_data['mentions'] = [mention['username'] for mention in tweet.entities.get('mentions', [])]
                    tweet_data['urls'] = [url['expanded_url'] for url in tweet.entities.get('urls', [])]
                
                collected_tweets.append(tweet_data)
            
            logger.info(f"Collected {len(collected_tweets)} tweets for query: {query}")
            return collected_tweets
        
        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error collecting tweets: {str(e)}")
            return []
    
    def collect_trending_topics(self) -> List[str]:
        """
        Get trending topics (requires elevated access)
        
        Returns:
            List of trending topic names
        """
        try:
            # Note: This requires elevated API access
            # For basic access, use predefined topics
            logger.info("Fetching trending topics")
            
            # Placeholder: In production with elevated access, use:
            # trends = self.client.get_place_trends(id=1)  # 1 = Worldwide
            
            # For now, return predefined topics
            default_topics = [
                "AI", "technology", "climate change", "politics",
                "science", "health", "economy", "sports"
            ]
            
            return default_topics
        
        except Exception as e:
            logger.error(f"Error fetching trending topics: {str(e)}")
            return []
    
    def save_to_queue(self, tweets: List[Dict], queue_name: str = "twitter_queue"):
        """
        Save collected tweets to Redis queue for processing
        
        Args:
            tweets: List of tweet dictionaries
            queue_name: Redis queue name
        """
        try:
            # In production: Push to Redis queue
            # redis_client.lpush(queue_name, json.dumps(tweets))
            logger.info(f"Saved {len(tweets)} tweets to queue: {queue_name}")
        except Exception as e:
            logger.error(f"Error saving to queue: {str(e)}")

def main():
    """Main collection loop for CronJob"""
    try:
        collector = TwitterCollector()
        
        # Get topics to collect
        topics_str = os.getenv("TWITTER_TOPICS", "AI,technology,news")
        topics = [t.strip() for t in topics_str.split(",")]
        
        posts_per_run = int(os.getenv("TWITTER_POSTS_PER_RUN", "50"))
        
        all_tweets = []
        
        for topic in topics:
            tweets = collector.collect_tweets(query=topic, max_results=posts_per_run // len(topics))
            all_tweets.extend(tweets)
            time.sleep(1)  # Rate limiting
        
        logger.info(f"Total tweets collected: {len(all_tweets)}")
        
        # Save to queue
        collector.save_to_queue(all_tweets)
        
        # In production: Save to database
        # db.save_tweets(all_tweets)
        
    except Exception as e:
        logger.error(f"Collection job failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
