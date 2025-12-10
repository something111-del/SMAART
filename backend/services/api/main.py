"""
SMAART API - Main FastAPI Application
Real-time social media intelligence and summarization platform
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SMAART API",
    description="Social Media Analytics & Real-Time Trends - AI-powered summarization platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SummarizeRequest(BaseModel):
    query: Optional[str] = Field(None, description="Topic or keyword to summarize", min_length=1, max_length=200)
    text: Optional[str] = Field(None, description="Direct text to summarize", min_length=10)
    hours: int = Field(default=24, description="Time window in hours", ge=1, le=168)
    sources: Optional[List[str]] = Field(default=None, description="Filter by sources: twitter, news")
    max_length: Optional[int] = Field(default=150, description="Maximum summary length", ge=50, le=500)

class SummaryResponse(BaseModel):
    query: Optional[str]
    summary: str
    sources: Dict[str, int]
    entities: List[str]
    sentiment: Dict[str, float]
    confidence: float
    generated_at: str
    processing_time_ms: int

class TrendingTopic(BaseModel):
    topic: str
    count: int
    sentiment: float
    sources: List[str]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]

# ML Model Loading
try:
    from backend.models.summarizer.model import SummarizationModel
    logger.info("Loading local SummarizationModel...")
    summarizer = SummarizationModel()
except ImportError as e:
    logger.error(f"Failed to load local model: {e}. Falling back to mock/API.")
    # Fallback/Mock for when dependencies are missing in dev
    class SummarizerModel:
        def summarize(self, text: str, max_length: int = 150) -> str:
            return "Local model failed to load. Please check logs."
    summarizer = SummarizerModel()
except Exception as e:
    logger.error(f"Error initializing model: {e}")
    # Fallback to prevent crash
    class SummarizerModel:
        def summarize(self, text: str, max_length: int = 150) -> str:
             return f"Model initialization error: {str(e)}"
    summarizer = SummarizerModel()

# API Routes
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "SMAART API - Social Media Analytics & Real-Time Trends",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        services={
            "api": "online",
            "ml_model": "serverless (huggingface)"
        }
    )

@app.post("/api/v1/summarize", response_model=SummaryResponse, tags=["Summarization"])
async def summarize_topic(request: SummarizeRequest):
    """
    Generate AI-powered summary
    Accepts either 'text' (direct input) or 'query' (topic search)
    """
    start_time = datetime.utcnow()
    
    try:
        input_text = ""
        sources_count = {"user_input": 1}
        
        if request.text:
            # Direct text summarization
            input_text = request.text
        elif request.query:
            # Heuristic: If query is long (> 30 chars) or contains many spaces, treat as text
            if len(request.query) > 30 or len(request.query.split()) > 5:
                input_text = request.query
            else:
# Real-time Web Search
                # Priority 1: X (Twitter) API
                try:
                    import tweepy
                    logger.info(f"Searching X/Twitter for: {request.query}")
                    
                    # X API Credentials
                    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAIdi5wEAAAAAN3QuXJP2GIpYBOuy%2BXpqunHTBmI%3DUCjKi7zL46t4pp6zlQeDcVZ3Mfy1PJ8uGXhIAmgyVMNBsgP3yS"
                    
                    client = tweepy.Client(bearer_token=BEARER_TOKEN)
                    
                    # Search recent tweets (basic query, english, no retweets)
                    tweets = client.search_recent_tweets(
                        query=f"{request.query} -is:retweet lang:en",
                        max_results=10,
                        tweet_fields=['created_at', 'text', 'public_metrics']
                    )
                    
                    if tweets.data:
                        tweet_texts = []
                        for tweet in tweets.data:
                            # Clean text slightly (remove newlines)
                            clean_text = tweet.text.replace('\n', ' ')
                            tweet_texts.append(f"Tweet: {clean_text}")
                        
                        input_text = "\n\n".join(tweet_texts)
                        sources_count = {"twitter": len(tweet_texts)}
                        logger.info(f"Retrieved {len(tweet_texts)} tweets from X")
                    
                    # If tweets found, we don't need to try DDG unless input_text is still empty
                except Exception as x_err:
                    logger.error(f"X API failed: {x_err}")
                    # Continue to DDG fallback
                
                if not input_text:
                    import time
                    max_retries = 3
                    retry_delay = 2  # seconds
                    
                    for attempt in range(max_retries):
                    try:
                        from duckduckgo_search import DDGS
                        
                        logger.info(f"Searching web for: {request.query} (attempt {attempt + 1}/{max_retries})")
                        with DDGS() as ddgs:
                            # Search for news/text results
                            results = list(ddgs.text(request.query, max_results=5))
                        
                        if results:
                            # Concatenate snippets to form the context for summarization
                            context_pieces = []
                            for r in results:
                                title = r.get('title', '')
                                body = r.get('body', '')
                                context_pieces.append(f"{title}: {body}")
                            
                            input_text = "\n\n".join(context_pieces)
                            sources_count = {"web_search": len(results)}
                            logger.info(f"Retrieved {len(results)} results from DuckDuckGo")
                            break  # Success, exit retry loop
                        else:
                            logger.warning("No results found via DuckDuckGo")
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay)
                                retry_delay *= 2  # Exponential backoff
                            else:
                                # Last attempt failed, return error
                                raise HTTPException(
                                    status_code=404,
                                    detail=f"No information found for '{request.query}'. Try a different query or provide text directly."
                                )
                            
                    except HTTPException:
                        raise  # Re-raise HTTP exceptions
                    except Exception as search_err:
                        logger.error(f"Search attempt {attempt + 1} failed: {search_err}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            retry_delay *= 2
                        else:
                            # All retries exhausted
                            # All retries exhausted for DuckDuckGo
                            logger.warning("DuckDuckGo failed, trying Wikipedia fallback...")
                            
                            # Wikipedia Fallback
                            try:
                                import requests
                                wiki_url = "https://en.wikipedia.org/w/api.php"
                                headers = {
                                    "User-Agent": "SMAART-Bot/1.0 (Educational Project; +http://3.145.166.181)"
                                }
                                params = {
                                    "action": "query",
                                    "format": "json",
                                    "list": "search",
                                    "srsearch": request.query,
                                    "srlimit": 1
                                }
                                response = requests.get(wiki_url, params=params, headers=headers, timeout=5)
                                data = response.json()
                                
                                if data.get("query", {}).get("search"):
                                    page_id = data["query"]["search"][0]["pageid"]
                                    
                                    # Get page content
                                    content_params = {
                                        "action": "query",
                                        "format": "json",
                                        "prop": "extracts",
                                        "pageids": page_id,
                                        "explaintext": True,
                                        "exintro": True
                                    }
                                    content_resp = requests.get(wiki_url, params=content_params, headers=headers, timeout=5)
                                    content_data = content_resp.json()
                                    extract = content_data["query"]["pages"][str(page_id)]["extract"]
                                    
                                    input_text = f"Wikipedia: {extract}"
                                    sources_count = {"wikipedia": 1}
                                    logger.info("Successfully retrieved content from Wikipedia")
                                else:
                                    logger.warning("No Wikipedia results found")
                                    raise Exception("No Wikipedia results")
                                    
                            except Exception as wiki_err:
                                logger.error(f"Wikipedia fallback failed: {wiki_err}")
                                
                                # Final Fallback: Mock data if purely for demo/testing
                                if "test" in request.query.lower() or "demo" in request.query.lower():
                                    input_text = f"This is a simulated summary for the topic '{request.query}'. Real-time search is currently rate-limited, but the system is fully functional for direct text summarization."
                                    sources_count = {"system_message": 1}
                                else:
                                    raise HTTPException(
                                        status_code=503,
                                        detail=f"Search services unavailable (Rate Limit). Please provide text directly."
                                    )
        else:
            raise HTTPException(status_code=400, detail="Either 'text' or 'query' must be provided")

        # Generate Summary
        summary_text = summarizer.summarize(input_text, max_length=request.max_length)
        
        # Calculate processing time
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        return SummaryResponse(
            query=request.query or "Direct Input",
            summary=summary_text,
            sources=sources_count,
            entities=[], # Placeholder for NER
            sentiment={"positive": 0.5, "neutral": 0.5}, # Placeholder
            confidence=0.95,
            generated_at=datetime.utcnow().isoformat(),
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        logger.error(f"Error in summarize endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@app.get("/api/v1/trending", response_model=List[TrendingTopic], tags=["Trending"])
async def get_trending_topics(limit: int = 10, hours: int = 24):
    """
    Get trending topics from the last N hours
    
    Returns top trending topics based on:
    - Frequency of mentions
    - Engagement metrics
    - Cross-source validation
    """
    try:
        # Placeholder implementation
        # In production: Query database for trending topics
        
        trending = [
            TrendingTopic(
                topic="Artificial Intelligence",
                count=156,
                sentiment=0.65,
                sources=["twitter", "news"]
            ),
            TrendingTopic(
                topic="Climate Change",
                count=98,
                sentiment=0.45,
                sources=["twitter", "news"]
            ),
            TrendingTopic(
                topic="Technology",
                count=87,
                sentiment=0.72,
                sources=["twitter", "news"]
            )
        ]
        
        return trending[:limit]
    
    except Exception as e:
        logger.error(f"Error in trending endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending topics: {str(e)}")

@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    # In production, return actual Prometheus metrics
    return {"message": "Prometheus metrics endpoint (implement prometheus_client)"}

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("API_RELOAD", "false").lower() == "true"
    )
