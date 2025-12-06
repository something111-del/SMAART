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

# ML Model Loading (Serverless Inference)
class SummarizerModel:
    """Hugging Face Inference API Wrapper (Serverless)"""
    
    def __init__(self):
        self.model_name = "facebook/bart-large-cnn"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.api_token = os.getenv("HF_API_TOKEN") # Optional, but recommended
        logger.info(f"Initializing HF Inference API for: {self.model_name}")
        import requests
        self.requests = requests
    
    def summarize(self, text: str, max_length: int = 150) -> str:
        """Generate summary via HF API"""
        if not text: return ""
        try:
            headers = {}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            
            payload = {
                "inputs": text,
                "parameters": {"max_length": max_length, "min_length": 30, "do_sample": False}
            }
            
            response = self.requests.post(self.api_url, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                # HF API returns a list of dictionaries
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("summary_text", "No summary generated.")
                return str(result)
            elif response.status_code == 503:
                return "Model is loading on Hugging Face (503). Please try again in 30 seconds."
            else:
                logger.error(f"HF API Error: {response.status_code} - {response.text}")
                return f"Summary failed: HF API {response.status_code}"
                
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return f"Error connecting to AI: {str(e)}"

# Initialize model
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
                # Simulated Topic Search (Mock DB)
                input_text = f"Recent news about {request.query} indicates significant market movement. Experts suggest caution while investors remain optimistic. Global events are influencing trends in {request.query}."
                sources_count = {"twitter": 10, "news": 5}
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
