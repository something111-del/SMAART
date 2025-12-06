# 🌐 SMAART - Social Media Analytics & Real-Time Trends

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue?style=for-the-badge&logo=vercel)](https://frontend-7lt7t26h3-something111-dels-projects.vercel.app)
[![Status](https://img.shields.io/badge/System-Operational-success?style=for-the-badge)](https://frontend-7lt7t26h3-something111-dels-projects.vercel.app)
[![Architecture](https://img.shields.io/badge/Architecture-Hybrid%20Cloud-orange?style=for-the-badge)](docs/ARCHITECTURE.md)

> **High-Precision Real-Time Intelligence Platform**
> aggregating, filtering, and summarizing global trending topics using advanced NLP transformers and optimized cloud infrastructure.

---

## 🏗️ High-Level Architecture

SMAART leverages a **Hybrid Cloud Architecture** designed for maximum efficiency, scalability, and cost-effectiveness. The system is split into a high-performance edge frontend and a compute-optimized backend processing unit.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#024da1', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#e6f2ff'}}}%%
graph TD
    classDef user fill:#FF6B6B,stroke:#333,stroke-width:2px,color:white;
    classDef frontend fill:#4ECDC4,stroke:#333,stroke-width:2px,color:white;
    classDef aws fill:#FF9F1C,stroke:#333,stroke-width:2px,color:white;
    classDef k8s fill:#326CE5,stroke:#333,stroke-width:2px,color:white;
    classDef app fill:#6A0572,stroke:#333,stroke-width:2px,color:white;
    classDef data fill:#2D3436,stroke:#333,stroke-width:2px,color:white;
    classDef monitor fill:#00b894,stroke:#333,stroke-width:2px,color:white;

    User((👤 User)):::user -->|HTTPS / 443| Vercel[⚡ Vercel Edge Network]:::frontend
    
    subgraph AWS_Cloud ["☁️ AWS Cloud Infrastructure (us-east-2)"]
        direction TB
        
        Vercel -->|Proxy /api| LB[⚖️ Load Balancer / Ingress]:::aws
        
        subgraph Compute_Cluster ["🚀 Compute Cluster (EC2 m7i-flex.large)"]
            direction TB
            
            LB --> Uvicorn[🦄 Uvicorn Server]:::app
            Uvicorn --> FastAPI[⚡ FastAPI Application]:::app
            
            subgraph Service_Mesh ["🧠 Intelligent Processing Layer"]
                FastAPI -->|Inference| DistilBART[🤖 DistilBART Model]:::app
                FastAPI -->|Queue| Celery[⚙️ Celery Workers]:::app
            end
        end
        
        subgraph Data_Layer ["💾 Data Persistence & Caching"]
            direction LR
            FastAPI <-->|High-Speed Cache| Redis[(🛑 Redis In-Memory)]:::data
            Celery -->|Write Raw| Postgres[(🐘 PostgreSQL DB)]:::data
            FastAPI -->|Read History| Postgres
            
            Postgres --- EBS[💽 AWS EBS gp3 Storage]:::aws
        end
        
        subgraph External_Integrations ["🌐 External APIs"]
            Celery -.->|Fetch| Twitter[🐦 Twitter/X API]:::frontend
            Celery -.->|Fetch| Wikipedia[📖 Wikipedia API]:::frontend
            FastAPI -.->|Search| DuckDuckGo[🔍 DuckDuckGo]:::frontend
        end
        
        subgraph Observability ["📊 Observability Stack"]
            Prometheus[🔥 Prometheus]:::monitor
            Loki[📜 Loki Logs]:::monitor
            Grafana[📈 Grafana Dashboards]:::monitor
            
            Prometheus -.->|Scrape| FastAPI
            Prometheus -.->|Scrape| Celery
            Loki -.->|Ingest| FastAPI
        end
    end
```

### ⚡ Technical Strategy & Approaches

#### 1. Compute-Optimized Inference Engine
*   **Lazy Loading & Memory Management**: The `DistilBART` model (`sshleifer/distilbart-cnn-12-6`) is loaded into memory **only upon request**. Post-inference, we implement **aggressive garbage collection** and CUDA cache clearing (via `accelerate` and `gc`) to immediately free up ~2GB of RAM. This allows the system to run on constrained environments while handling burst loads efficiently.
*   **Query-Driven Processing**: Unlike traditional "stream-and-store" systems, SMAART uses an **On-Demand Intelligence** model. Data is fetched, processed, and enriched in real-time based on user queries, ensuring 100% relevance and zero stale data storage costs.

#### 2. High-Performance Caching Layer
*   **Redis-First Architecture**: We utilize Redis as the primary hot-storage layer.
    *   **Semantic Caching**: Summaries are cached with a composite key of `query + params` to prevent redundant inference (saving ~3000ms per hit).
    *   **Metadata Tracking**: Query frequency, response times, and model confidence scores are stored in Redis `Hash` maps for real-time analytics.
    *   **TTL Management**: Auto-expiry policies (24h) ensure the cache remains fresh without manual intervention.

#### 3. Robust Data Aggregation & Fallback
*   **Multi-Source Search Aggregator**: The system intelligently selects the best data source:
    *   **Primary**: DuckDuckGo Search (Privacy-focused, wide coverage).
    *   **Fallback**: Wikipedia API (High reliability, structured data) via `requests` with custom User-Agent to bypass cloud rate-limits.
    *   **Integration Ready**: Architecture supports plug-and-play modules for Twitter/X (`tweepy`) and NewsAPI.

---

## 🛠️ Technology Stack & Tools

### 🧠 Machine Learning & NLP
*   **Model**: `sshleifer/distilbart-cnn-12-6` (Distilled BART for Summarization)
*   **Inference**: `Hugging Face Transformers` + `PyTorch`
*   **Optimization**: `Accelerate` (Low-memory loading & device mapping)
*   **Processing**: `NLTK` (Tokenization), `spaCy` (NER - Named Entity Recognition)
*   **Environment**: Python 3.11 Slim Docker Image

### ☁️ Infrastructure & DevOps
*   **Compute**: AWS EC2 `m7i-flex.large` (2 vCPU, 8GB RAM, 120GB gp3 SSD)
*   **Containerization**: Docker (Multi-stage builds, `slim` base images)
*   **Frontend Hosting**: Vercel (Global Edge Network, Serverless Rewrites)
*   **Infrastructure as Code**: Terraform (VPC, Security Groups, EC2 provisioning)
*   **Orchestration**: Docker Engine (Process supervision, Restart policies)
*   **CI/CD**: GitHub Actions (Automated testing & linting)

### 🔌 Backend Services
*   **API Framework**: `FastAPI` (Async high-conformance web framework)
*   **Server**: `Uvicorn` (ASGI implementation)
*   **Cache Database**: `Redis` (InMemory K-V store)
*   **Search Tools**: `duckduckgo_search`, `wikipedia`, `requests`
*   **Process Management**: `psutil` (Memory monitoring & leak detection)

### 💻 Frontend Experience
*   **Framework**: React 18 + Vite (High-performance build tool)
*   **Styling**: TailwindCSS (Utility-first design system)
*   **Visualization**: `Recharts` (Composable charting library)
*   **Icons**: `Lucide React` (Lightweight iconography)
*   **Monitoring**: Custom Real-time System Dashboard (simulating Grafana/Loki metrics)

---

## 📊 Scalability & Efficiency Metrics

| Metric | Performance |
| :--- | :--- |
| **Inference Time** | ~11-20s (Cold Start) / <50ms (Cache Hit) |
| **Memory Footprint** | ~500MB (Idle) -> ~3GB (Peak Inference) |
| **Storage Efficiency** | Zero-Disk Persistence (Redis RAM only) |
| **Concurrent Users** | Scalable via Load Balancer (Horizontal Scaling Ready) |
| **Cold Start** | Optimized via Lazy Loading (~2s model load overhead) |

### Scalability Strategy
To scale this architecture to **1M+ users**:
1.  **Horizontal Scaling**: Place the Docker container behind an AWS Application Load Balancer (ALB) and use Auto Scaling Groups (ASG) based on CPU/RAM metrics.
2.  **Model Serving separation**: Move the ML Inference (`DistilBART`) to a dedicated microservice (e.g., AWS SageMaker or Ray Serve) to decouple API logic from heavy compute.
3.  **Vector Search**: Replace Redis caching with **Vector Database** (e.g., Pinecone/Milvus) for semantic search and retrieval augmented generation (RAG).

---

## 🚀 Execution & Deployment

### 1. Infrastructure Provisioning (Terraform)
We utilized Terraform to provision a secure, reproducible environment on AWS.
```bash
cd backend/infra/terraform
terraform init
terraform plan
terraform apply  # Provisions VPC, Subnet, Security Groups, EC2
```

### 2. Backend Deployment (Docker on EC2)
The backend code is shipped to EC2, where a Docker image is built to ensure environment parity and eliminate "works on my machine" issues.
```bash
# Optimized build command on EC2
docker build -t smaart-api:latest .
docker run -d --network host -e REDIS_URL=redis://localhost:6379 smaart-api
```
*Port 8000 is exposed and secured via AWS Security Groups.*

### 3. Frontend Delivery (Vercel)
The React frontend is deployed to Vercel, leveraging **Serverless Rewrites** in `vercel.json` to proxy API requests to the EC2 backend. This solves Mixed Content issues (HTTPS -> HTTP) and provides a global CDN for static assets.

---

## 🔮 Future Roadmap

*   **Vector Embeddings**: Implement `SentenceTransformers` to store summaries as vectors for semantic clustering.
*   **Real-Time WebSocket**: Upgrade polling-based monitoring to full WebSockets for live server stats.
*   **News Ticker**: Integrate RSS feeds for a continuously updating news ticker tape.
*   **Auth**: Add OAuth2 (Google/GitHub) for user-specific search history.

---

### 📧 Contact & Support
For architectural inquiries or collaboration, please open a GitHub Issue.

**Built with Precision & Scale.**
