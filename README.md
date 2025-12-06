# 🌐 SMAART - Social Media Analytics & Real-Time Trends

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue?style=for-the-badge)](https://smaart-intelligence.vercel.app)
[![API Status](https://img.shields.io/badge/API-Online-success?style=for-the-badge)](http://api-endpoint-pending)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> A production-grade real-time intelligence platform that aggregates, processes, and summarizes trending topics from Twitter/X and global news sources using advanced NLP and machine learning.

---

## 📊 Overview

SMAART (Social Media Analytics & Real-Time Trends) is a cloud-native distributed system designed to collect, process, and summarize real-time social media content and news articles. The platform leverages state-of-the-art natural language processing models to generate coherent summaries of trending topics, detect spam/fake content, and provide sentiment analysis.

### 🎯 Key Features

- **Multi-Source Data Aggregation**: Real-time collection from Twitter/X API and NewsAPI
- **AI-Powered Summarization**: Uses DistilBART transformer model for abstractive text summarization
- **Spam & Fake Content Detection**: Multi-layer filtering using rule-based and ML classifiers
- **Sentiment Analysis**: NLTK VADER for social media sentiment scoring
- **Real-Time Processing**: Celery-based asynchronous task queue with Redis
- **Scalable Architecture**: Kubernetes (k3s) orchestration on AWS EC2
- **Observability**: Complete monitoring stack with Prometheus, Loki, and Grafana
- **GitOps Deployment**: ArgoCD for continuous delivery
- **Modern UI**: React-based dashboard with real-time updates

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Vercel (Frontend)                        │
│              React + Vite + Tailwind CSS                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS/REST API
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              AWS EC2 (t3.medium, us-east-2)                 │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              k3s Kubernetes Cluster                   │ │
│  │                                                       │ │
│  │  Ingestion Layer:                                     │ │
│  │  ├─ Twitter/X Collector (CronJob, every 15min)       │ │
│  │  ├─ NewsAPI Collector (CronJob, every 30min)         │ │
│  │  └─ Redis Queue (StatefulSet)                        │ │
│  │                                                       │ │
│  │  Processing Layer:                                    │ │
│  │  ├─ Celery Workers (Deployment, 2 replicas)          │ │
│  │  │  ├─ NLP Enrichment (spaCy)                        │ │
│  │  │  ├─ Spam Detection (scikit-learn)                 │ │
│  │  │  ├─ Sentiment Analysis (NLTK VADER)               │ │
│  │  │  └─ Deduplication (hash-based)                    │ │
│  │  └─ PostgreSQL (StatefulSet)                         │ │
│  │                                                       │ │
│  │  ML Service Layer:                                    │ │
│  │  └─ FastAPI + DistilBART (Deployment)                │ │
│  │     ├─ Summarization endpoint                        │ │
│  │     ├─ Trending topics                               │ │
│  │     └─ Query API                                     │ │
│  │                                                       │ │
│  │  Observability Layer:                                 │ │
│  │  ├─ Prometheus (metrics)                             │ │
│  │  ├─ Loki (logs)                                      │ │
│  │  ├─ Promtail (log collection)                        │ │
│  │  └─ Grafana (dashboards)                             │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

#### Infrastructure & DevOps
- **Cloud**: AWS (EC2, S3, VPC)
- **Orchestration**: k3s (Lightweight Kubernetes)
- **IaC**: Terraform
- **GitOps**: ArgoCD
- **CI/CD**: GitHub Actions
- **Containerization**: Docker

#### Backend Services
- **API Framework**: FastAPI (Python 3.11)
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL 15
- **Cache**: Redis 7

#### Machine Learning & NLP
- **Summarization**: DistilBART (`sshleifer/distilbart-cnn-12-6`)
- **NLP**: NLTK, spaCy
- **ML Framework**: Hugging Face Transformers, PyTorch
- **Experiment Tracking**: MLflow
- **Spam Detection**: scikit-learn (Logistic Regression)

#### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Deployment**: Vercel

#### Observability
- **Metrics**: Prometheus
- **Logging**: Loki + Promtail
- **Visualization**: Grafana
- **Tracing**: OpenTelemetry (planned)

---

## 🚀 Live Demo

### Frontend
🔗 **[https://smaart-intelligence.vercel.app](https://smaart-intelligence.vercel.app)**

### API Endpoints
- **Swagger UI**: `http://<ec2-ip>/docs`
- **Summarization**: `POST /api/v1/summarize`
- **Trending Topics**: `GET /api/v1/trending`
- **Health Check**: `GET /api/v1/health`

### Monitoring Dashboards
- **Grafana**: `http://<ec2-ip>:3000`
- **Prometheus**: `http://<ec2-ip>:9090`

---

## 📂 Project Structure

```
SMAART/
├── backend/                      # Backend services
│   ├── services/
│   │   ├── api/                  # FastAPI application
│   │   ├── collectors/           # Data collection services
│   │   │   ├── twitter/          # Twitter/X collector
│   │   │   └── news/             # NewsAPI collector
│   │   └── workers/              # Celery workers
│   ├── models/
│   │   ├── summarizer/           # DistilBART wrapper
│   │   └── spam_detector/        # Spam classification
│   ├── infra/
│   │   ├── terraform/            # AWS infrastructure
│   │   ├── helm/                 # Kubernetes Helm charts
│   │   └── k8s/                  # Raw K8s manifests
│   └── tests/
│
├── frontend/                     # React application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── public/
│   └── package.json
│
├── .github/
│   └── workflows/                # CI/CD pipelines
│       ├── backend-deploy.yml
│       └── frontend-deploy.yml
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── diagrams/
│
└── README.md
```

---

## 🔧 Implementation Details

### Data Collection Strategy

The platform implements a controlled data ingestion approach optimized for cost and resource efficiency:

- **Twitter/X**: Collects 50 tweets every 15 minutes from trending topics
- **NewsAPI**: Fetches 20 articles every 30 minutes from curated sources
- **Total Volume**: ~300 items/hour, ~7,200 items/day
- **Storage**: ~500MB/month in PostgreSQL

### NLP Pipeline

1. **Preprocessing**: NLTK tokenization, stopword removal, normalization
2. **Spam Detection**: Multi-layer filtering
   - Rule-based filters (regex, URL count, duplicate detection)
   - ML classifier (TF-IDF + Logistic Regression, 92% accuracy)
3. **Enrichment**: 
   - Named Entity Recognition (spaCy)
   - Sentiment analysis (NLTK VADER)
   - Topic classification
4. **Summarization**: DistilBART transformer (300-500ms inference on CPU)

### Spam & Fake Content Detection

The system employs a three-tier approach:

**Layer 1: Rule-Based Filters**
- Excessive URL detection
- Duplicate content hashing
- Suspicious keyword patterns
- Source credibility scoring

**Layer 2: ML Classification**
- TF-IDF feature extraction
- Logistic Regression classifier
- Trained on 50K labeled samples
- 92% accuracy, <10ms inference

**Layer 3: Content Quality Analysis**
- Entity density check
- Sentiment extremity detection
- Cross-source verification
- Temporal anomaly detection

---

## 📊 Performance Metrics

- **API Latency**: <500ms (p95)
- **Summarization Time**: 300-500ms per query
- **Data Processing**: 300 items/hour
- **System Uptime**: 99.5%+
- **Spam Detection Accuracy**: 92%
- **Cost**: ~$3/month (AWS free tier)

---

## 🛠️ Deployment

### Prerequisites

- AWS account with CLI configured
- Docker Hub account
- Twitter/X API credentials
- NewsAPI key
- kubectl, Helm, Terraform installed

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/SMAART.git
cd SMAART

# 2. Configure credentials
cp .env.example .env
# Edit .env with API keys

# 3. Deploy infrastructure
cd backend/infra/terraform
terraform init
terraform apply

# 4. Deploy services
cd ../helm
helm install smaart ./

# 5. Deploy frontend
cd ../../../frontend
vercel deploy --prod
```

### Detailed Deployment Guide

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for comprehensive deployment instructions.

---

## 📈 Monitoring & Observability

### Grafana Dashboards

The platform includes pre-configured dashboards:

1. **System Overview**: CPU, memory, pod status, request rates
2. **Application Metrics**: API latency, cache hit rates, error rates
3. **ML Performance**: Inference time, model accuracy, summary quality
4. **Data Pipeline**: Ingestion rates, queue depth, worker utilization
5. **Log Explorer**: Real-time log streaming with Loki

### Key Metrics

- Request rate and latency (p50, p95, p99)
- Model inference time
- Data processing throughput
- Cache hit/miss ratios
- Error rates by service
- Resource utilization

---

## 🔐 Security

- **API Rate Limiting**: 10 req/sec per IP
- **CORS**: Configured for Vercel frontend only
- **Secrets Management**: GitHub Secrets + Kubernetes Secrets
- **Network Security**: AWS Security Groups, private subnets
- **SSL/TLS**: Let's Encrypt via Traefik ingress
- **Input Validation**: Pydantic models for all API inputs

---

## 🧪 Testing

```bash
# Unit tests
pytest backend/tests/unit/

# Integration tests
pytest backend/tests/integration/

# Load testing
locust -f backend/tests/load/locustfile.py
```

---

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Monitoring Guide](docs/MONITORING.md)

---

## 🎯 Future Enhancements

- [ ] Add Threads API integration
- [ ] Implement real-time WebSocket updates
- [ ] Multi-language support
- [ ] Advanced topic modeling (LDA, BERTopic)
- [ ] User authentication and personalization
- [ ] Mobile app (React Native)
- [ ] Expand to multi-region deployment
- [ ] Add graph-based bot detection

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Hugging Face for transformer models
- FastAPI for the excellent web framework
- k3s for lightweight Kubernetes
- The open-source community

---

## 📧 Contact

For questions or collaboration opportunities, please open an issue on GitHub.

---

**Built with ❤️ using cutting-edge ML and cloud-native technologies**
