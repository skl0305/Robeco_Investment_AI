# Robeco AI Investment Analysis System - Technical Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [API Reference](#api-reference)
4. [AI Agent System](#ai-agent-system)
5. [Document Generation](#document-generation)
6. [Database Schema](#database-schema)
7. [Configuration](#configuration)
8. [Deployment](#deployment)
9. [Performance](#performance)
10. [Security](#security)

## System Architecture

### Overview
The Robeco AI Investment Analysis System is an enterprise-grade platform that combines **AI-powered financial analysis** with **real-time streaming capabilities** and **professional document generation**. Built on a modern FastAPI backend with WebSocket streaming, it delivers institutional-quality investment research through a scalable, multi-agent architecture.

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                    Robeco AI Investment Platform                │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Layer                                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │  Web Interface  │ │   WebSocket     │ │   Document      │   │
│  │   (Professional │ │   Streaming     │ │   Export        │   │
│  │    Workbench)   │ │                 │ │                 │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │  Professional   │ │   WebSocket     │ │   Document      │   │
│  │      API        │ │    Handler      │ │   Conversion    │   │
│  │  (/api/prof...) │ │     (/ws)       │ │   (Word/PDF)    │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  AI Agent System                                               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │  12 Specialist  │ │   Google        │ │   Real-time     │   │
│  │    Analysts     │ │   Research      │ │   Streaming     │   │
│  │                 │ │   Integration   │ │                 │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                     │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   Financial     │ │   Google        │ │   Document      │   │
│  │   Data (yf)     │ │   Gemini AI     │ │   Templates     │   │
│  │                 │ │   (115+ keys)   │ │                 │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Principles
- **Real-time Streaming**: Token-by-token content delivery via WebSockets
- **Multi-Agent Architecture**: 12 specialized AI analysts working in coordination
- **Enterprise Scalability**: 115+ API key management for high concurrency
- **Professional Document Generation**: Word and PDF export with exact formatting
- **Financial Data Integration**: Comprehensive market data with yfinance
- **Robust Error Handling**: Automatic failover and recovery mechanisms

## Core Components

### 1. Main Application (`/src/robeco/backend/main.py`)
```python
# FastAPI application with comprehensive middleware
app = FastAPI(
    title="Robeco AI Investment Analysis System",
    version="2.0.0",
    description="Professional AI-powered investment research platform"
)

# Key configurations:
- CORS middleware for cross-origin requests
- WebSocket support for real-time streaming
- Health check endpoints
- Auto-reload in development mode
- Port: 8001 (configurable)
```

### 2. Professional API Layer (`/src/robeco/backend/professional_api.py`)

#### Analyst Team Structure
```python
ANALYST_TEAM = {
    "chief": "Chief Investment Officer - Strategic oversight and synthesis",
    "fundamentals": "Fundamental Analyst - Financial health and valuation",
    "industry": "Industry Analyst - Sector dynamics and competitive position", 
    "technical": "Technical Analyst - Chart patterns and market momentum",
    "risk": "Risk Management Analyst - Risk assessment and mitigation",
    "esg": "ESG Analyst - Environmental, social, and governance factors",
    "research": "Research Analyst - Market research and data analysis",
    "sentiment": "Market Sentiment Analyst - Investor psychology and sentiment",
    "management": "Management Analyst - Leadership and corporate governance",
    "business": "Business Model Analyst - Revenue streams and business strategy",
    "valuation": "Valuation Analyst - Asset pricing and valuation models",
    "macro": "Macro Economist - Economic trends and market conditions"
}
```

#### Key API Endpoints
```python
@app.websocket("/ws/professional")
async def websocket_professional_endpoint(websocket: WebSocket)

@app.post("/api/professional/analyze")
async def analyze_with_professional_analyst(request: AnalysisRequest)

@app.post("/api/professional/report")
async def generate_comprehensive_report(request: ReportRequest)

@app.post("/api/professional/convert")
async def convert_document(request: ConversionRequest)
```

### 3. AI Agent System (`/src/robeco/agents/streaming_professional_analyst.py`)

#### Streaming Professional Analyst
```python
class StreamingProfessionalAnalyst:
    def __init__(self, analyst_type: str):
        self.analyst_type = analyst_type
        self.websocket = None
        self.gemini_model = None
        
    async def analyze_with_streaming(
        self, 
        ticker: str, 
        company_name: str, 
        websocket: WebSocket,
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Real-time token-by-token streaming analysis
        # Google research integration
        # Professional formatting and structure
```

#### Key Features
- **Token-by-Token Streaming**: Real-time content delivery as AI generates analysis
- **Google Research Integration**: Live web research with source credibility scoring
- **Specialist Expertise**: Each analyst has unique focus areas and analytical frameworks
- **Professional Output**: Structured investment-grade analysis format

### 4. Financial Data Integration (`/src/robeco/data/yfinance_fetcher.py`)

```python
class YFinanceFetcher:
    def fetch_comprehensive_data(self, ticker: str) -> Dict[str, Any]:
        return {
            "basic_info": self._fetch_basic_info(ticker),
            "price_data": self._fetch_current_pricing(ticker),
            "financial_statements": self._fetch_financial_data(ticker),
            "ratios": self._calculate_financial_ratios(ticker),
            "analyst_coverage": self._fetch_analyst_estimates(ticker),
            "technical_indicators": self._calculate_technical_metrics(ticker)
        }
```

#### Comprehensive Data Coverage
- **Real-time Pricing**: Current price, volume, market cap
- **Financial Statements**: Income statement, balance sheet, cash flow
- **Financial Ratios**: P/E, P/B, ROE, debt ratios, margin analysis
- **Analyst Coverage**: Estimates, recommendations, price targets
- **Technical Analysis**: Moving averages, volatility, momentum indicators
- **Company Fundamentals**: Business description, sector, industry classification

## API Reference

### WebSocket Streaming Protocol

#### Connection
```javascript
const ws = new WebSocket('ws://localhost:8001/ws/professional');
```

#### Message Types

**Inbound Messages (Client → Server)**
```javascript
// Start individual analyst analysis
{
  "type": "start_analysis",
  "data": {
    "ticker": "AAPL",
    "company": "Apple Inc.",
    "analyst": "fundamentals",
    "data_sources": { /* financial data */ }
  }
}

// Generate comprehensive report
{
  "type": "generate_report", 
  "data": {
    "analyses_data": { /* all completed analyses */ }
  }
}
```

**Outbound Messages (Server → Client)**
```javascript
// Analysis started confirmation
{
  "type": "streaming_analysis_started",
  "data": {
    "analyst": "fundamentals",
    "status": "Analysis initiated",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}

// Real-time AI content streaming
{
  "type": "streaming_ai_content",
  "data": {
    "content": "Based on Apple's latest quarterly results...",
    "analyst": "fundamentals",
    "complete": false
  }
}

// Research source found
{
  "type": "streaming_research_source",
  "data": {
    "title": "Apple Inc. Q3 2024 Earnings Analysis",
    "url": "https://example.com/apple-q3-analysis",
    "credibility": "high",
    "summary": "Detailed quarterly analysis..."
  }
}

// Analysis completion
{
  "type": "analysis_complete",
  "data": {
    "analyst": "fundamentals",
    "full_analysis": "/* complete analysis text */",
    "research_sources": [/* array of sources */],
    "timestamp": "2024-01-01T12:05:00Z"
  }
}
```

### REST API Endpoints

#### Analysis Endpoints
```http
POST /api/professional/analyze
Content-Type: application/json

{
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "analyst_type": "fundamentals",
  "analysis_data": { /* yfinance data */ }
}
```

#### Document Conversion
```http
POST /api/professional/convert
Content-Type: application/json

{
  "html_content": "<html>...</html>",
  "format": "word",  // or "pdf"
  "company_name": "Apple Inc.",
  "ticker": "AAPL"
}
```

#### System Status
```http
GET /health
Response: {
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "2.0.0"
}

GET /api/professional/analysts
Response: {
  "available_analysts": 12,
  "analyst_types": ["chief", "fundamentals", ...],
  "system_status": "operational"
}
```

## AI Agent System

### Analyst Specializations

#### 1. **Chief Investment Officer**
- **Focus**: Strategic oversight, portfolio implications, investment recommendations
- **Output**: Executive summary, key investment thesis, risk-reward assessment
- **Integration**: Synthesizes insights from all other analysts

#### 2. **Fundamental Analyst**  
- **Focus**: Financial health, valuation metrics, earnings quality
- **Output**: DCF models, P/E analysis, financial strength assessment
- **Data Sources**: Financial statements, ratios, historical performance

#### 3. **Industry Analyst**
- **Focus**: Sector dynamics, competitive positioning, market trends  
- **Output**: Industry comparison, competitive advantages, market share analysis
- **Research**: Industry reports, competitor analysis, market sizing

#### 4. **Technical Analyst**
- **Focus**: Chart patterns, momentum indicators, trading signals
- **Output**: Technical outlook, support/resistance levels, trend analysis
- **Indicators**: Moving averages, RSI, MACD, volume analysis

#### 5. **Risk Management Analyst**
- **Focus**: Risk assessment, scenario analysis, downside protection
- **Output**: Risk metrics, stress testing, correlation analysis
- **Framework**: VaR, beta analysis, drawdown assessment

### Analysis Workflow

```python
# Sequential analysis flow
analysis_pipeline = [
    "fundamentals",  # Financial foundation
    "industry",      # Market context  
    "technical",     # Price action
    "risk",          # Risk assessment
    "valuation",     # Pricing models
    "esg",           # Sustainability factors
    "management",    # Leadership quality
    "business",      # Business model
    "sentiment",     # Market psychology
    "macro",         # Economic environment
    "research",      # Additional research
    "chief"          # Strategic synthesis
]
```

## Document Generation

### Word Document Export (`/src/robeco/backend/word_report_generator.py`)

#### Features
- **Exact Layout Preservation**: Maintains HTML formatting in Word
- **Professional Styling**: Robeco brand colors, fonts, and spacing
- **Complex Table Handling**: Financial data tables with proper alignment
- **Chart Integration**: SVG charts converted to high-quality images
- **Multi-Page Support**: Automatic page breaks and section formatting

#### Technical Implementation
```python
class RobecoWordReportGenerator:
    def __init__(self):
        self.temp_images_to_cleanup = []
        self.image_cache = {}
        
    async def convert_html_to_word(
        self, 
        html_content: str, 
        company_name: str, 
        ticker: str,
        output_path: Optional[str] = None
    ) -> str:
        # Parse HTML with BeautifulSoup
        # Convert SVG charts to PNG images using Puppeteer
        # Generate Word document with python-docx
        # Apply Robeco professional styling
        # Return path to generated document
```

#### Chart Conversion Pipeline
```python
# SVG → Image conversion process
1. Extract SVG elements from HTML
2. Create temporary HTML file with isolated SVG
3. Use Puppeteer to render SVG as PNG
4. Embed high-quality image in Word document  
5. Clean up temporary files
```

### PDF Generation (`/src/robeco/backend/enhanced_pdf_service.py`)

#### Custom A4 Format
```python
CUSTOM_A4_SETTINGS = {
    'width_mm': 426,
    'height_mm': 603,
    'dpi': 96,
    'width_px': 1620,
    'height_px': 2291
}
```

#### Puppeteer Configuration
```javascript
// PDF generation script
const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
});

await page.pdf({
    path: outputPath,
    width: '426mm',
    height: '603mm',
    printBackground: true,
    preferCSSPageSize: false
});
```

## Database Schema

### Core Tables (SQLite/PostgreSQL)

#### Projects Table
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    retry_count INTEGER DEFAULT 0,
    last_retry_at TIMESTAMP,
    error_message TEXT
);
```

#### Analyses Table  
```sql
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    analyst_type VARCHAR(50) NOT NULL,
    analysis_content TEXT,
    research_sources JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'completed'
);
```

#### API Keys Management
```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY,
    key_name VARCHAR(100) NOT NULL,
    key_value VARCHAR(255) NOT NULL,
    provider VARCHAR(50) DEFAULT 'gemini',
    status VARCHAR(50) DEFAULT 'active',
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    rate_limit_reset TIMESTAMP
);
```

## Configuration

### Environment Configuration (`/src/robeco/core/config.py`)

```python
class Settings:
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = True
    
    # AI Configuration  
    MAX_CONCURRENT_AGENTS: int = 12
    STREAMING_CHUNK_SIZE: int = 50
    ANALYSIS_TIMEOUT: int = 300
    
    # API Rate Limiting
    API_RATE_LIMIT: int = 60  # requests per minute
    WEBSOCKET_TIMEOUT: int = 300
    
    # Document Generation
    PDF_FORMAT: str = "A4_CUSTOM"
    WORD_TEMPLATE: str = "professional"
    
    # Network Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:8001",
        "http://172.20.10.2:8005"
    ]
```

### API Key Management

#### Primary Key Configuration
```python
# Primary API key (highest priority)
PRIMARY_KEY_FILE = "primary_gemini_key.txt"

# Backup key pool (115+ keys)
BACKUP_KEYS_FILE = "gemini_api_keys.txt" 

# Environment variable support
GEMINI_API_KEY_1 through GEMINI_API_KEY_12
```

#### Key Rotation Logic
```python
class APIKeyManager:
    def __init__(self):
        self.primary_key = self._load_primary_key()
        self.backup_keys = self._load_backup_keys()
        self.current_key_index = 0
        self.failed_keys = set()
        
    async def get_active_key(self) -> str:
        # Try primary key first
        # Rotate through backup keys on failure
        # Track failed keys for recovery
        # Implement exponential backoff
```

## Deployment

### System Requirements

```yaml
# Minimum Requirements
Python: ">=3.8"
Node.js: ">=16.0"  
Memory: "4GB RAM"
Storage: "10GB available space"
Network: "Stable internet connection"

# Recommended Requirements  
Python: ">=3.11"
Node.js: ">=18.0"
Memory: "8GB RAM"
Storage: "50GB SSD"
CPU: "4+ cores"
```

### Installation Process

```bash
# 1. Clone repository
git clone <repository-url>
cd "Robeco Reporting"

# 2. Python environment setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Node.js dependencies  
npm install

# 5. Install Puppeteer Chrome browser
npx puppeteer browsers install chrome

# 6. Configure API keys
# Add Gemini API keys to primary_gemini_key.txt and gemini_api_keys.txt

# 7. Initialize database
python src/robeco/database/init_db.py

# 8. Start the system
python run_professional_system.py
```

### Production Deployment

#### Using Gunicorn
```bash
# Install production server
pip install gunicorn

# Start with multiple workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  --timeout 300 \
  src.robeco.backend.main:app
```

#### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Node.js for Puppeteer
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

COPY . .
RUN npm install
RUN npx puppeteer browsers install chrome

EXPOSE 8001
CMD ["python", "run_professional_system.py"]
```

### Environment Variables

```bash
# Production configuration
export ROBECO_ENV=production
export DATABASE_URL=postgresql://user:pass@localhost/robeco
export SECRET_KEY=your-production-secret-key
export GEMINI_API_KEY_1=your-primary-api-key

# Scaling configuration  
export MAX_CONCURRENT_AGENTS=20
export WEBSOCKET_TIMEOUT=600
export API_RATE_LIMIT=120
```

## Performance

### Scalability Features

#### Multi-Key Management
- **115+ API Keys**: Supports high-volume concurrent analysis
- **Intelligent Load Balancing**: Optimal key distribution across requests
- **Automatic Failover**: Seamless switching on key suspension/limits
- **Usage Tracking**: Monitors key health and performance

#### Real-time Streaming Optimization
```python
# Streaming performance settings
STREAMING_CONFIG = {
    "chunk_size": 50,           # Tokens per chunk
    "delay_ms": 100,            # Delay between chunks  
    "max_concurrent": 12,       # Simultaneous analyses
    "buffer_size": 1024,        # WebSocket buffer
    "compression": True         # Gzip compression
}
```

#### Caching Strategy
- **Analysis Results**: localStorage persistence for repeat access
- **Financial Data**: Intelligent caching with expiration
- **Document Templates**: Pre-compiled template caching
- **API Response Caching**: Redis integration for production

### Memory Management

```python
# Automatic cleanup mechanisms
class MemoryManager:
    def __init__(self):
        self.active_analyses = {}
        self.temp_files = []
        
    async def cleanup_completed_analysis(self, analysis_id: str):
        # Clear analysis data from memory
        # Remove temporary files
        # Update usage metrics
        
    def monitor_memory_usage(self):
        # Track memory consumption
        # Implement garbage collection triggers
        # Log performance metrics
```

### Performance Monitoring

```python
# Built-in performance tracking
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(f"Request {request.url} completed in {process_time:.2f}s")
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Security

### Authentication & Authorization

```python
# JWT token-based authentication
class SecurityManager:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.algorithm = "HS256"
        self.token_expire_minutes = 60
        
    def create_access_token(self, data: dict):
        # Generate JWT token with expiration
        
    def verify_token(self, token: str):
        # Validate and decode JWT token
```

### API Key Security

```python
# Secure API key storage and rotation
class APIKeyVault:
    def __init__(self):
        self.encrypted_keys = self._load_encrypted_keys()
        self.key_rotation_schedule = 24  # hours
        
    def encrypt_api_key(self, key: str) -> str:
        # Use cryptography library for encryption
        
    def decrypt_api_key(self, encrypted_key: str) -> str:
        # Secure decryption with error handling
```

### Input Validation

```python
# Comprehensive input validation
class InputValidator:
    @staticmethod
    def validate_ticker(ticker: str) -> str:
        # Sanitize ticker symbols
        # Prevent injection attacks
        
    @staticmethod  
    def validate_html_content(content: str) -> str:
        # HTML sanitization
        # Remove malicious scripts
        # Preserve safe formatting
```

### Rate Limiting & DDoS Protection

```python
# Request rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/professional/analyze")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def analyze_endpoint(request: Request):
    # Protected endpoint with rate limiting
```

### Data Protection

```python
# Sensitive data handling
class DataProtection:
    @staticmethod
    def sanitize_financial_data(data: dict) -> dict:
        # Remove or encrypt sensitive information
        # Implement data retention policies
        
    @staticmethod
    def audit_log_access(user_id: str, resource: str):
        # Log all data access for compliance
        # Implement GDPR compliance measures
```

---

## Maintenance & Monitoring

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "2.0.0",
        "active_analyses": len(active_websocket_connections),
        "api_keys_status": "operational"
    }
```

### Logging Configuration
```python
import structlog

# Structured logging setup
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

### Error Tracking
```python
# Comprehensive error handling and reporting
class ErrorTracker:
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.recent_errors = deque(maxlen=100)
        
    async def log_error(self, error: Exception, context: dict):
        # Log error with full context
        # Track error patterns
        # Implement alerting for critical errors
```

This technical documentation provides a comprehensive overview of the Robeco AI Investment Analysis System's architecture, implementation, and deployment requirements. The system is designed for enterprise-grade performance with robust error handling, security measures, and scalability features.