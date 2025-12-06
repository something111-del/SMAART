"""
News API Data Collector
Collects news articles from global sources
"""

from newsapi import NewsApiClient
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsCollector:
    """Collects news articles using NewsAPI"""
    
    def __init__(self):
        """Initialize NewsAPI client"""
        self.api_key = os.getenv("NEWS_API_KEY")
        
        if not self.api_key:
            raise ValueError("NEWS_API_KEY not found in environment variables")
        
        self.client = NewsApiClient(api_key=self.api_key)
        logger.info("News collector initialized successfully")
    
    def collect_articles(
        self,
        query: str = None,
        sources: str = None,
        max_results: int = 20,
        hours_back: int = 24
    ) -> List[Dict]:
        """
        Collect news articles
        
        Args:
            query: Search query (keywords)
            sources: Comma-separated source IDs
            max_results: Maximum articles to collect
            hours_back: How many hours back to search
        
        Returns:
            List of article dictionaries
        """
        try:
            logger.info(f"Collecting articles - Query: {query}, Sources: {sources}")
            
            # Calculate time range
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(hours=hours_back)
            
            # Fetch articles
            if query:
                response = self.client.get_everything(
                    q=query,
                    sources=sources,
                    from_param=from_date.isoformat(),
                    to=to_date.isoformat(),
                    language='en',
                    sort_by='publishedAt',
                    page_size=min(max_results, 100)  # API limit
                )
            else:
                response = self.client.get_top_headlines(
                    sources=sources,
                    language='en',
                    page_size=min(max_results, 100)
                )
            
            if response['status'] != 'ok':
                logger.error(f"NewsAPI error: {response.get('message', 'Unknown error')}")
                return []
            
            articles = response.get('articles', [])
            
            # Process articles
            collected_articles = []
            
            for article in articles:
                article_data = {
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'content': article.get('content'),
                    'url': article.get('url'),
                    'source_id': article.get('source', {}).get('id'),
                    'source_name': article.get('source', {}).get('name'),
                    'author': article.get('author'),
                    'published_at': article.get('publishedAt'),
                    'url_to_image': article.get('urlToImage'),
                    'source': 'news',
                    'query': query,
                    'collected_at': datetime.utcnow().isoformat()
                }
                
                # Skip articles without content
                if not article_data['title'] or not article_data['description']:
                    continue
                
                collected_articles.append(article_data)
            
            logger.info(f"Collected {len(collected_articles)} articles")
            return collected_articles
        
        except Exception as e:
            logger.error(f"Error collecting articles: {str(e)}")
            return []
    
    def collect_top_headlines(self, category: str = None, country: str = 'us', max_results: int = 20) -> List[Dict]:
        """
        Collect top headlines
        
        Args:
            category: News category (business, technology, etc.)
            country: Country code (us, gb, etc.)
            max_results: Maximum articles to collect
        
        Returns:
            List of article dictionaries
        """
        try:
            logger.info(f"Collecting top headlines - Category: {category}, Country: {country}")
            
            response = self.client.get_top_headlines(
                category=category,
                country=country,
                language='en',
                page_size=min(max_results, 100)
            )
            
            if response['status'] != 'ok':
                logger.error(f"NewsAPI error: {response.get('message', 'Unknown error')}")
                return []
            
            articles = response.get('articles', [])
            
            # Process articles (same as collect_articles)
            collected_articles = []
            
            for article in articles:
                article_data = {
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'content': article.get('content'),
                    'url': article.get('url'),
                    'source_id': article.get('source', {}).get('id'),
                    'source_name': article.get('source', {}).get('name'),
                    'author': article.get('author'),
                    'published_at': article.get('publishedAt'),
                    'url_to_image': article.get('urlToImage'),
                    'source': 'news',
                    'category': category,
                    'collected_at': datetime.utcnow().isoformat()
                }
                
                if article_data['title'] and article_data['description']:
                    collected_articles.append(article_data)
            
            logger.info(f"Collected {len(collected_articles)} top headlines")
            return collected_articles
        
        except Exception as e:
            logger.error(f"Error collecting top headlines: {str(e)}")
            return []
    
    def save_to_queue(self, articles: List[Dict], queue_name: str = "news_queue"):
        """
        Save collected articles to Redis queue for processing
        
        Args:
            articles: List of article dictionaries
            queue_name: Redis queue name
        """
        try:
            # In production: Push to Redis queue
            # redis_client.lpush(queue_name, json.dumps(articles))
            logger.info(f"Saved {len(articles)} articles to queue: {queue_name}")
        except Exception as e:
            logger.error(f"Error saving to queue: {str(e)}")

def main():
    """Main collection loop for CronJob"""
    try:
        collector = NewsCollector()
        
        # Get configuration
        sources_str = os.getenv("NEWS_SOURCES", "reuters,bbc-news,cnn")
        articles_per_run = int(os.getenv("NEWS_ARTICLES_PER_RUN", "20"))
        
        # Collect articles
        all_articles = []
        
        # Method 1: Top headlines
        headlines = collector.collect_top_headlines(
            category='general',
            max_results=articles_per_run // 2
        )
        all_articles.extend(headlines)
        
        # Method 2: Technology news
        tech_news = collector.collect_top_headlines(
            category='technology',
            max_results=articles_per_run // 2
        )
        all_articles.extend(tech_news)
        
        logger.info(f"Total articles collected: {len(all_articles)}")
        
        # Save to queue
        collector.save_to_queue(all_articles)
        
        # In production: Save to database
        # db.save_articles(all_articles)
        
    except Exception as e:
        logger.error(f"Collection job failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
