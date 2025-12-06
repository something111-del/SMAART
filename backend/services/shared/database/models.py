"""
Database Models
SQLAlchemy ORM models for PostgreSQL
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class RawPost(Base):
    """Raw posts from collectors (Twitter, News)"""
    __tablename__ = 'raw_posts'
    
    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False)  # 'twitter' or 'news'
    external_id = Column(String(255), unique=True)  # Tweet ID or article URL
    content = Column(Text, nullable=False)
    title = Column(String(500))
    author = Column(String(255))
    url = Column(String(1000))
    metadata = Column(JSON)  # Additional data (likes, retweets, etc.)
    collected_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    enriched_post = relationship("EnrichedPost", back_populates="raw_post", uselist=False)
    
    def __repr__(self):
        return f"<RawPost(id={self.id}, source='{self.source}', title='{self.title[:50]}...')>"


class EnrichedPost(Base):
    """Enriched posts after NLP processing"""
    __tablename__ = 'enriched_posts'
    
    id = Column(Integer, primary_key=True)
    raw_post_id = Column(Integer, ForeignKey('raw_posts.id'), unique=True)
    
    # NLP results
    entities = Column(JSON)  # Named entities extracted
    sentiment = Column(JSON)  # Sentiment scores {positive, neutral, negative}
    topics = Column(JSON)  # Classified topics
    keywords = Column(JSON)  # Extracted keywords
    
    # Spam detection
    is_spam = Column(Boolean, default=False)
    spam_confidence = Column(Float)
    
    # Quality metrics
    quality_score = Column(Float)  # Overall content quality (0-1)
    readability_score = Column(Float)
    
    # Processing metadata
    processed_at = Column(DateTime, default=datetime.utcnow)
    processing_time_ms = Column(Integer)  # Time taken to process
    
    # Relationship
    raw_post = relationship("RawPost", back_populates="enriched_post")
    features = relationship("FeatureVector", back_populates="enriched_post", uselist=False)
    
    def __repr__(self):
        return f"<EnrichedPost(id={self.id}, is_spam={self.is_spam}, quality={self.quality_score})>"


class FeatureVector(Base):
    """Feature vectors for ML models"""
    __tablename__ = 'feature_vectors'
    
    id = Column(Integer, primary_key=True)
    enriched_post_id = Column(Integer, ForeignKey('enriched_posts.id'), unique=True)
    
    # TF-IDF features (stored as JSON array)
    tfidf_vector = Column(JSON)
    
    # Embedding features (if using BERT/etc)
    embedding_vector = Column(JSON)
    
    # Metadata features
    text_length = Column(Integer)
    word_count = Column(Integer)
    sentence_count = Column(Integer)
    avg_word_length = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    enriched_post = relationship("EnrichedPost", back_populates="features")
    
    def __repr__(self):
        return f"<FeatureVector(id={self.id}, text_length={self.text_length})>"


class Query(Base):
    """User queries and generated summaries"""
    __tablename__ = 'queries'
    
    id = Column(Integer, primary_key=True)
    query_text = Column(String(500), nullable=False)
    
    # Query parameters
    time_window_hours = Column(Integer, default=24)
    sources_filter = Column(JSON)  # List of sources to include
    
    # Results
    summary = Column(Text)
    sources_count = Column(JSON)  # Count by source
    entities = Column(JSON)  # Key entities in summary
    sentiment = Column(JSON)  # Overall sentiment
    confidence = Column(Float)  # Model confidence
    
    # Metadata
    posts_analyzed = Column(Integer)  # Number of posts used
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Query(id={self.id}, query='{self.query_text}', posts={self.posts_analyzed})>"


class TrendingTopic(Base):
    """Trending topics cache"""
    __tablename__ = 'trending_topics'
    
    id = Column(Integer, primary_key=True)
    topic = Column(String(255), nullable=False)
    
    # Metrics
    mention_count = Column(Integer, default=0)
    sentiment_score = Column(Float)  # Average sentiment
    velocity = Column(Float)  # Rate of growth
    
    # Sources
    sources = Column(JSON)  # List of sources mentioning this topic
    
    # Time window
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TrendingTopic(topic='{self.topic}', mentions={self.mention_count})>"


# Database initialization
def init_db(engine):
    """Initialize database tables"""
    Base.metadata.create_all(engine)
    print("Database tables created successfully")


if __name__ == "__main__":
    from sqlalchemy import create_engine
    
    # Create engine (example)
    engine = create_engine('sqlite:///smaart.db', echo=True)
    
    # Create tables
    init_db(engine)
