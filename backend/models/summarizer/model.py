"""
Memory-Efficient DistilBART Summarization Model with Redis Caching
Lazy-loading model with intelligent caching and automatic cleanup
"""

import os
import gc
import json
import hashlib
import torch
import redis
import logging
from typing import Optional, List, Dict
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SummarizationModel:
    """
    Memory-efficient summarization model with Redis caching
    
    Features:
    - Lazy loading: Model only loaded when needed
    - Redis caching: Stores summaries and embeddings
    - Automatic cleanup: Model unloaded after each request
    - Query-driven: Only processes what's requested
    - Cache expiration: Auto-cleanup of old entries
    """
    
    def __init__(
        self, 
        model_name: str = "sshleifer/distilbart-cnn-12-6",
        redis_url: str = None
    ):
        """
        Initialize the summarization model (lazy - doesn't load model yet)
        
        Args:
            model_name: Hugging Face model identifier
            redis_url: Redis connection URL (defaults to env var)
        """
        self.model_name = model_name
        self.device = "cpu"  # Force CPU to save memory
        self._model = None
        self._tokenizer = None
        self._summarizer = None
        
        # Initialize Redis connection
        redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.redis_client.ping()
            logger.info("✅ Redis connected successfully")
            self.cache_enabled = True
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Running without cache.")
            self.redis_client = None
            self.cache_enabled = False
        
        # Cache settings
        self.cache_ttl = 86400  # 24 hours
        self.cache_prefix = "smaart:summary:"
        
        logger.info(f"SummarizationModel initialized (lazy mode, cache: {self.cache_enabled})")
    
    def _generate_cache_key(self, text: str, max_length: int, min_length: int) -> str:
        """
        Generate a unique cache key for the input
        
        Args:
            text: Input text
            max_length: Max summary length
            min_length: Min summary length
            
        Returns:
            Cache key string
        """
        # Create hash of input parameters
        content = f"{text}:{max_length}:{min_length}"
        hash_obj = hashlib.sha256(content.encode())
        return f"{self.cache_prefix}{hash_obj.hexdigest()}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """
        Retrieve summary from Redis cache
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached summary or None
        """
        if not self.cache_enabled:
            return None
        
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.info("✅ Cache HIT - returning cached summary")
                # Update TTL on access
                self.redis_client.expire(cache_key, self.cache_ttl)
                return cached
            else:
                logger.info("❌ Cache MISS - will generate new summary")
                return None
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
    
    def _save_to_cache(self, cache_key: str, summary: str):
        """
        Save summary to Redis cache
        
        Args:
            cache_key: Cache key
            summary: Summary to cache
        """
        if not self.cache_enabled:
            return
        
        try:
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                summary
            )
            logger.info("💾 Summary saved to cache")
        except Exception as e:
            logger.error(f"Cache save error: {e}")
    
    def _save_query_metadata(self, query_hash: str, metadata: Dict):
        """
        Save query metadata (for analytics and learning)
        
        Args:
            query_hash: Query hash
            metadata: Metadata dictionary
        """
        if not self.cache_enabled:
            return
        
        try:
            meta_key = f"smaart:meta:{query_hash}"
            self.redis_client.setex(
                meta_key,
                self.cache_ttl,
                json.dumps(metadata)
            )
            
            # Track query frequency
            freq_key = f"smaart:freq:{query_hash}"
            self.redis_client.incr(freq_key)
            self.redis_client.expire(freq_key, self.cache_ttl)
            
        except Exception as e:
            logger.error(f"Metadata save error: {e}")
    
    @contextmanager
    def _load_model_context(self):
        """
        Context manager that loads model, yields it, then cleans up
        This ensures model is only in memory during actual inference
        """
        try:
            # Load model if not already loaded
            if self._model is None or self._tokenizer is None:
                logger.info(f"📥 Loading model: {self.model_name}")
                
                # Load with minimal memory footprint
                self._tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    model_max_length=512  # Limit context length
                )
                
                self._model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,  # Use float32 for CPU
                    low_cpu_mem_usage=True      # Optimize memory usage
                )
                
                self._model.to(self.device)
                self._model.eval()  # Set to evaluation mode
                
                # Create pipeline
                self._summarizer = pipeline(
                    "summarization",
                    model=self._model,
                    tokenizer=self._tokenizer,
                    device=-1,  # CPU
                    framework="pt"
                )
                
                logger.info("✅ Model loaded successfully")
            
            yield self._summarizer
            
        finally:
            # Cleanup after use
            self._cleanup()
    
    def _cleanup(self):
        """
        Aggressive cleanup to free memory after inference
        """
        logger.info("🧹 Cleaning up model from memory...")
        
        # Delete model components
        if self._summarizer is not None:
            del self._summarizer
            self._summarizer = None
        
        if self._model is not None:
            del self._model
            self._model = None
        
        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None
        
        # Clear PyTorch cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Force garbage collection
        gc.collect()
        
        logger.info("✅ Memory cleanup complete")
    
    def summarize(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 50,
        do_sample: bool = False,
        force_refresh: bool = False
    ) -> str:
        """
        Generate summary from text (with caching)
        
        Args:
            text: Input text to summarize
            max_length: Maximum summary length
            min_length: Minimum summary length
            do_sample: Whether to use sampling
            force_refresh: Skip cache and regenerate
            
        Returns:
            Generated summary
        """
        try:
            # Truncate input if too long to save memory
            max_input_length = 1024
            if len(text) > max_input_length:
                logger.warning(f"Input text truncated from {len(text)} to {max_input_length} chars")
                text = text[:max_input_length]
            
            # Generate cache key
            cache_key = self._generate_cache_key(text, max_length, min_length)
            
            # Check cache first (unless force refresh)
            if not force_refresh:
                cached_summary = self._get_from_cache(cache_key)
                if cached_summary:
                    return cached_summary
            
            # Use context manager to ensure cleanup
            with self._load_model_context() as summarizer:
                logger.info("🔄 Generating summary...")
                
                # Generate summary with memory-efficient settings
                result = summarizer(
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=do_sample,
                    truncation=True,
                    clean_up_tokenization_spaces=True
                )
                
                summary = result[0]['summary_text']
                logger.info(f"✅ Summary generated (length: {len(summary)})")
                
                # Save to cache
                self._save_to_cache(cache_key, summary)
                
                # Save metadata for learning
                query_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
                self._save_query_metadata(query_hash, {
                    "input_length": len(text),
                    "output_length": len(summary),
                    "max_length": max_length,
                    "min_length": min_length,
                    "compression_ratio": len(text) / len(summary) if len(summary) > 0 else 0
                })
                
                return summary
                
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            # Ensure cleanup even on error
            self._cleanup()
            raise
    
    def batch_summarize(
        self,
        texts: List[str],
        max_length: int = 150,
        min_length: int = 50
    ) -> List[str]:
        """
        Summarize multiple texts (processes one at a time with caching)
        
        Args:
            texts: List of input texts
            max_length: Maximum summary length
            min_length: Minimum summary length
            
        Returns:
            List of summaries
        """
        logger.info(f"📦 Batch summarizing {len(texts)} texts (sequential with cache)")
        
        summaries = []
        for i, text in enumerate(texts):
            try:
                logger.info(f"Processing text {i+1}/{len(texts)}")
                summary = self.summarize(text, max_length, min_length)
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Error processing text {i+1}: {str(e)}")
                summaries.append(f"Error: {str(e)}")
        
        return summaries
    
    def clear_cache(self, pattern: str = None):
        """
        Clear cache entries
        
        Args:
            pattern: Optional pattern to match (default: all summaries)
        """
        if not self.cache_enabled:
            logger.warning("Cache not enabled")
            return
        
        try:
            pattern = pattern or f"{self.cache_prefix}*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"🗑️ Cleared {len(keys)} cache entries")
            else:
                logger.info("No cache entries to clear")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        if not self.cache_enabled:
            return {"cache_enabled": False}
        
        try:
            summary_keys = self.redis_client.keys(f"{self.cache_prefix}*")
            meta_keys = self.redis_client.keys("smaart:meta:*")
            freq_keys = self.redis_client.keys("smaart:freq:*")
            
            return {
                "cache_enabled": True,
                "cached_summaries": len(summary_keys),
                "metadata_entries": len(meta_keys),
                "frequency_tracking": len(freq_keys),
                "cache_ttl_seconds": self.cache_ttl
            }
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {"error": str(e)}
    
    def get_memory_usage(self) -> Dict[str, float]:
        """
        Get current memory usage statistics
        
        Returns:
            Dictionary with memory usage info
        """
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            "model_loaded": self._model is not None,
            "cache_enabled": self.cache_enabled
        }


# Singleton instance for reuse across requests
_model_instance: Optional[SummarizationModel] = None


def get_model() -> SummarizationModel:
    """
    Get or create singleton model instance
    
    Returns:
        SummarizationModel instance
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = SummarizationModel()
    return _model_instance


# Example usage
if __name__ == "__main__":
    # Initialize model (lazy - doesn't load yet)
    model = SummarizationModel()
    
    # Test summarization
    test_text = """
    Artificial intelligence is rapidly transforming various industries. 
    Machine learning algorithms are being deployed in healthcare, finance, 
    and transportation. Recent breakthroughs in natural language processing 
    have enabled more sophisticated chatbots and translation systems. 
    However, concerns about AI ethics and job displacement remain significant 
    challenges that need to be addressed.
    """
    
    print("Before summarization:")
    print(f"Memory usage: {model.get_memory_usage()}")
    print(f"Cache stats: {model.get_cache_stats()}")
    
    # First call - will load model and generate
    summary1 = model.summarize(test_text, max_length=100)
    print(f"\nSummary 1: {summary1}")
    
    # Second call with same text - should use cache
    summary2 = model.summarize(test_text, max_length=100)
    print(f"\nSummary 2 (cached): {summary2}")
    
    print("\nAfter summarization (model should be unloaded):")
    print(f"Memory usage: {model.get_memory_usage()}")
    print(f"Cache stats: {model.get_cache_stats()}")
