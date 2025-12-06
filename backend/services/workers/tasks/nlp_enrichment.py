"""
NLP Enrichment Task
Extracts entities, sentiment, and topics from text
"""

from celery import Task
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
import spacy
import logging

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

def enrich_post(post_data):
    """
    Enrich post with NLP analysis
    
    Args:
        post_data: Dictionary with post content
        
    Returns:
        Dictionary with enrichment data
    """
    text = post_data.get('content', '') or post_data.get('text', '')
    
    if not text:
        return {}
    
    enrichment = {}
    
    try:
        # 1. Sentiment Analysis
        sentiment_scores = sia.polarity_scores(text)
        enrichment['sentiment'] = {
            'positive': sentiment_scores['pos'],
            'neutral': sentiment_scores['neu'],
            'negative': sentiment_scores['neg'],
            'compound': sentiment_scores['compound']
        }
        
        # 2. Named Entity Recognition
        if nlp:
            doc = nlp(text[:1000])  # Limit to 1000 chars for performance
            entities = {}
            for ent in doc.ents:
                entity_type = ent.label_
                if entity_type not in entities:
                    entities[entity_type] = []
                if ent.text not in entities[entity_type]:
                    entities[entity_type].append(ent.text)
            
            enrichment['entities'] = entities
            enrichment['entity_list'] = [ent.text for ent in doc.ents]
        else:
            enrichment['entities'] = {}
            enrichment['entity_list'] = []
        
        # 3. Keywords extraction (simple frequency-based)
        tokens = word_tokenize(text.lower())
        stopwords = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'])
        keywords = [w for w in tokens if w.isalnum() and w not in stopwords and len(w) > 3]
        
        # Get top 10 most frequent
        from collections import Counter
        keyword_freq = Counter(keywords)
        enrichment['keywords'] = [word for word, count in keyword_freq.most_common(10)]
        
        # 4. Text statistics
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        enrichment['statistics'] = {
            'char_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0
        }
        
        # 5. Quality score (simple heuristic)
        quality_score = 0.0
        
        # Has entities
        if enrichment.get('entity_list'):
            quality_score += 0.3
        
        # Reasonable length
        if 50 < len(words) < 500:
            quality_score += 0.3
        
        # Not too many special characters
        special_char_ratio = sum(not c.isalnum() and not c.isspace() for c in text) / len(text)
        if special_char_ratio < 0.1:
            quality_score += 0.2
        
        # Has multiple sentences
        if len(sentences) > 2:
            quality_score += 0.2
        
        enrichment['quality_score'] = min(quality_score, 1.0)
        
        logger.info(f"Enrichment complete: {len(enrichment.get('entity_list', []))} entities, quality={enrichment['quality_score']:.2f}")
        
    except Exception as e:
        logger.error(f"Enrichment error: {str(e)}")
        enrichment['error'] = str(e)
    
    return enrichment


if __name__ == "__main__":
    # Test
    test_post = {
        'content': "Apple Inc. announced new iPhone features today in California. CEO Tim Cook presented the innovations to investors."
    }
    
    result = enrich_post(test_post)
    print("Enrichment result:")
    print(result)
