# SMAART Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Deployment Architecture](#deployment-architecture)
7. [Scalability & Performance](#scalability--performance)
8. [Security](#security)

---

## System Overview

SMAART is a cloud-native, microservices-based platform designed to aggregate, process, and summarize real-time social media content and news articles. The system leverages advanced NLP models to generate coherent summaries, detect spam/fake content, and provide sentiment analysis.

### Design Principles

- **Microservices Architecture**: Loosely coupled services for independent scaling
- **Event-Driven Processing**: Asynchronous task processing with Celery + Redis
- **Cloud-Native**: Kubernetes orchestration for portability and scalability
- **Cost-Optimized**: Designed to run within AWS free tier constraints
- **Observable**: Comprehensive monitoring with Prometheus, Loki, and Grafana

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        External APIs                            │
│         Twitter/X API          NewsAPI          GDELT           │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                     AWS EC2 (t3.medium)                         │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              k3s Kubernetes Cluster                       │ │
│  │                                                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  Ingestion Layer (Namespace: ingestion)             │ │ │
│  │  │                                                     │ │ │
│  │  │  ┌──────────────┐      ┌──────────────┐           │ │ │
│  │  │  │ Twitter      │      │ News         │           │ │ │
│  │  │  │ Collector    │      │ Collector    │           │ │ │
│  │  │  │ (CronJob)    │      │ (CronJob)    │           │ │ │
│  │  │  │ Every 15min  │      │ Every 30min  │           │ │ │
│  │  │  └──────┬───────┘      └──────┬───────┘           │ │ │
│  │  │         │                     │                   │ │ │
│  │  │         └──────────┬──────────┘                   │ │ │
│  │  │                    ↓                              │ │ │
│  │  │         ┌──────────────────────┐                  │ │ │
│  │  │         │  Redis Queue         │                  │ │ │
│  │  │         │  (StatefulSet)       │                  │ │ │
│  │  │         │  - Pub/Sub           │                  │ │ │
│  │  │         │  - Cache             │                  │ │ │
│  │  │         └──────────┬───────────┘                  │ │ │
│  │  └────────────────────┼──────────────────────────────┘ │ │
│  │                       │                                │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  Processing Layer (Namespace: processing)       │  │ │
│  │  │                    ↓                            │  │ │
│  │  │  ┌──────────────────────────────────────────┐   │  │ │
│  │  │  │  Celery Workers (Deployment, 2 replicas) │   │  │ │
│  │  │  │                                          │   │  │ │
│  │  │  │  Tasks:                                  │   │  │ │
│  │  │  │  - NLP Enrichment (spaCy)                │   │  │ │
│  │  │  │  - Spam Detection (ML classifier)        │   │  │ │
│  │  │  │  - Sentiment Analysis (NLTK VADER)       │   │  │ │
│  │  │  │  - Deduplication (hash-based)            │   │  │ │
│  │  │  │  - Entity Extraction                     │   │  │ │
│  │  │  └──────────────────┬───────────────────────┘   │  │ │
│  │  │                     ↓                           │  │ │
│  │  │  ┌──────────────────────────────────────────┐   │  │ │
│  │  │  │  PostgreSQL (StatefulSet)                │   │  │ │
│  │  │  │                                          │   │  │ │
│  │  │  │  Tables:                                 │   │  │ │
│  │  │  │  - raw_posts                             │   │  │ │
│  │  │  │  - enriched_posts                        │   │  │ │
│  │  │  │  - features                              │   │  │ │
│  │  │  │  - queries                               │   │  │ │
│  │  │  └──────────────────────────────────────────┘   │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │                                                        │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  ML Service Layer (Namespace: ml-service)       │  │ │
│  │  │                                                 │  │ │
│  │  │  ┌──────────────────────────────────────────┐   │  │ │
│  │  │  │  FastAPI + DistilBART (Deployment)       │   │  │ │
│  │  │  │                                          │   │  │ │
│  │  │  │  Endpoints:                              │   │  │ │
│  │  │  │  - POST /api/v1/summarize                │   │  │ │
│  │  │  │  - GET /api/v1/trending                  │   │  │ │
│  │  │  │  - GET /api/v1/health                    │   │  │ │
│  │  │  │  - GET /metrics (Prometheus)             │   │  │ │
│  │  │  └──────────────────────────────────────────┘   │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │                       ↑                                │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  Ingress Layer (Namespace: ingress)             │  │ │
│  │  │                                                 │  │ │
│  │  │  ┌──────────────────────────────────────────┐   │  │ │
│  │  │  │  Traefik Ingress (built-in k3s)          │   │  │ │
│  │  │  │                                          │   │  │ │
│  │  │  │  Features:                               │   │  │ │
│  │  │  │  - SSL/TLS (Let's Encrypt)               │   │  │ │
│  │  │  │  - Rate limiting (10 req/sec)            │   │  │ │
│  │  │  │  - Path-based routing                    │   │  │ │
│  │  │  │  - CORS handling                         │   │  │ │
│  │  │  └──────────────────────────────────────────┘   │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │                                                        │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  Observability (Namespace: monitoring)          │  │ │
│  │  │                                                 │  │ │
│  │  │  ┌────────────┐  ┌────────────┐  ┌──────────┐  │  │ │
│  │  │  │ Prometheus │  │   Loki     │  │ Promtail │  │  │ │
│  │  │  │ (metrics)  │  │  (logs)    │  │(collect) │  │  │ │
│  │  │  └────────────┘  └────────────┘  └──────────┘  │  │ │
│  │  │                                                 │  │ │
│  │  │  ┌────────────┐                                 │  │ │
│  │  │  │  Grafana   │                                 │  │ │
│  │  │  │(dashboards)│                                 │  │ │
│  │  │  └────────────┘                                 │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          ↑
                          │ HTTPS/REST API
                          │
┌─────────────────────────────────────────────────────────────┐
│                    Vercel (Frontend)                        │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              React + Vite Application                 │ │
│  │                                                       │ │
│  │  Components:                                          │ │
│  │  - SearchBar (query input)                            │ │
│  │  - SummaryCard (AI-generated summary)                 │ │
│  │  - TrendingTopics (clickable topic cards)             │ │
│  │  - SentimentChart (visualization)                     │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Data Collection Layer

#### Twitter Collector
- **Technology**: Python + Tweepy
- **Schedule**: CronJob every 15 minutes
- **Volume**: 50 tweets per run (~200/hour)
- **Features**:
  - Topic-based collection
  - Rate limit handling
  - Metadata extraction (likes, retweets, author info)

#### News Collector
- **Technology**: Python + NewsAPI client
- **Schedule**: CronJob every 30 minutes
- **Volume**: 20 articles per run (~40/hour)
- **Features**:
  - Category filtering
  - Source selection
  - Content extraction

### 2. Message Queue (Redis)
- **Purpose**: Decouple collection from processing
- **Features**:
  - Pub/Sub for task distribution
  - Cache for API responses
  - Session storage
- **Configuration**: Single instance, 256MB memory

### 3. Processing Layer

#### Celery Workers
- **Replicas**: 2 workers
- **Concurrency**: 4 tasks per worker
- **Tasks**:
  1. **NLP Enrichment**: spaCy for entity extraction
  2. **Spam Detection**: ML classifier (92% accuracy)
  3. **Sentiment Analysis**: NLTK VADER
  4. **Deduplication**: SHA-256 hash comparison
  5. **Feature Extraction**: TF-IDF vectors

#### PostgreSQL Database
- **Schema**:
  ```sql
  -- Raw posts from collectors
  CREATE TABLE raw_posts (
      id SERIAL PRIMARY KEY,
      source VARCHAR(50),  -- 'twitter' or 'news'
      content TEXT,
      metadata JSONB,
      collected_at TIMESTAMP,
      created_at TIMESTAMP DEFAULT NOW()
  );

  -- Enriched posts after processing
  CREATE TABLE enriched_posts (
      id SERIAL PRIMARY KEY,
      raw_post_id INTEGER REFERENCES raw_posts(id),
      entities JSONB,  -- Named entities
      sentiment JSONB,  -- Sentiment scores
      is_spam BOOLEAN,
      quality_score FLOAT,
      processed_at TIMESTAMP
  );

  -- Feature vectors for ML
  CREATE TABLE features (
      id SERIAL PRIMARY KEY,
      post_id INTEGER REFERENCES enriched_posts(id),
      feature_vector FLOAT[],
      created_at TIMESTAMP DEFAULT NOW()
  );

  -- User queries and results
  CREATE TABLE queries (
      id SERIAL PRIMARY KEY,
      query TEXT,
      summary TEXT,
      sources JSONB,
      sentiment JSONB,
      confidence FLOAT,
      created_at TIMESTAMP DEFAULT NOW()
  );
  ```

### 4. ML Service Layer

#### FastAPI Application
- **Model**: DistilBART (sshleifer/distilbart-cnn-12-6)
- **Inference**: CPU-only, 300-500ms latency
- **Endpoints**:
  - `POST /api/v1/summarize`: Generate summary
  - `GET /api/v1/trending`: Get trending topics
  - `GET /api/v1/health`: Health check
  - `GET /metrics`: Prometheus metrics

#### Summarization Pipeline
```python
1. Query database for relevant posts
2. Filter by time window and sources
3. Aggregate text content
4. Preprocess with NLTK
5. Run through DistilBART
6. Extract entities with spaCy
7. Calculate sentiment with VADER
8. Return structured response
```

### 5. Frontend (React)
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Features**:
  - Real-time search
  - Trending topics display
  - Sentiment visualization
  - Responsive design

---

## Data Flow

### Collection Flow
```
1. CronJob triggers collector
2. Collector fetches data from API
3. Data pushed to Redis queue
4. Celery worker picks up task
5. Worker processes data (NLP, spam detection)
6. Enriched data saved to PostgreSQL
7. Cache updated in Redis
```

### Query Flow
```
1. User submits query via React UI
2. Frontend calls FastAPI endpoint
3. API queries PostgreSQL
4. Relevant posts aggregated
5. Text preprocessed
6. DistilBART generates summary
7. Entities extracted, sentiment calculated
8. Response returned to frontend
9. UI displays results
```

---

## Technology Stack

### Infrastructure
- **Cloud**: AWS EC2 (t3.medium, us-east-2)
- **Orchestration**: k3s (Lightweight Kubernetes)
- **IaC**: Terraform
- **GitOps**: ArgoCD
- **CI/CD**: GitHub Actions

### Backend
- **API**: FastAPI (Python 3.11)
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL 15
- **Cache**: Redis 7

### Machine Learning
- **Summarization**: DistilBART (Hugging Face Transformers)
- **NLP**: NLTK, spaCy
- **ML Framework**: PyTorch, scikit-learn
- **Experiment Tracking**: MLflow

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Deployment**: Vercel

### Observability
- **Metrics**: Prometheus
- **Logging**: Loki + Promtail
- **Visualization**: Grafana
- **Alerting**: Prometheus Alertmanager

---

## Deployment Architecture

### Infrastructure as Code (Terraform)
```hcl
# EC2 instance
resource "aws_instance" "smaart" {
  ami           = "ami-0c55b159cbfafe1f0"  # Ubuntu 22.04
  instance_type = "t3.medium"
  
  user_data = file("k3s-install.sh")
  
  tags = {
    Name = "smaart-k3s-node"
  }
}

# Security group
resource "aws_security_group" "smaart" {
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### GitOps with ArgoCD
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: smaart
spec:
  project: default
  source:
    repoURL: https://github.com/yourusername/SMAART
    targetRevision: main
    path: backend/infra/helm
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

---

## Scalability & Performance

### Current Capacity
- **Throughput**: 300 items/hour
- **API Latency**: <500ms (p95)
- **Concurrent Users**: ~50
- **Storage**: ~500MB/month

### Scaling Strategy
1. **Horizontal Pod Autoscaling**: Scale workers based on queue depth
2. **Database Read Replicas**: Add PostgreSQL replicas for read queries
3. **Redis Cluster**: Shard cache across multiple nodes
4. **Multi-Region**: Deploy to additional AWS regions

### Performance Optimizations
- **Caching**: Redis cache for frequent queries (1-hour TTL)
- **Database Indexing**: B-tree indexes on query columns
- **Connection Pooling**: SQLAlchemy connection pool
- **Async I/O**: FastAPI async endpoints

---

## Security

### Network Security
- **VPC**: Private subnets for database and workers
- **Security Groups**: Whitelist only necessary ports
- **SSL/TLS**: Let's Encrypt certificates via Traefik

### Application Security
- **API Rate Limiting**: 10 requests/second per IP
- **CORS**: Restricted to Vercel frontend domain
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM

### Secrets Management
- **Kubernetes Secrets**: Encrypted at rest
- **GitHub Secrets**: For CI/CD credentials
- **Environment Variables**: Never committed to Git

### Monitoring & Alerting
- **Prometheus Alerts**: High memory, API errors, worker failures
- **Log Analysis**: Loki for security event detection
- **Audit Logs**: All API requests logged

---

## Cost Analysis

### Monthly Costs
| Service | Configuration | Cost |
|---------|--------------|------|
| EC2 | t3.medium (750 hrs free tier) | $0 |
| S3 | 10GB storage | $2-3 |
| Data Transfer | 5GB/month | $0 (100GB free) |
| **Total** | | **~$3/month** |

### Cost Optimization
- **Free Tier Maximization**: All services within AWS free tier
- **Spot Instances**: Use for non-critical workloads (future)
- **S3 Lifecycle Policies**: Archive old data to Glacier
- **Resource Limits**: Kubernetes resource quotas prevent overuse

---

**Last Updated**: December 2024  
**Version**: 1.0.0
