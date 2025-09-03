# Robeco Professional Investment Analysis Platform

A production-grade institutional investment research platform powered by ultra-sophisticated multi-agent AI architecture. Built for portfolio managers, investment analysts, and institutional decision-makers requiring comprehensive, real-time investment intelligence with professional-grade sourcing and analysis depth.

## System Architecture

### Core Components

**Backend Services**
- **Ultra-Sophisticated Multi-Agent Engine**: Sequential intelligence deployment with cross-agent synthesis
- **Professional Streaming Server**: Real-time WebSocket-based analysis delivery 
- **Bulk File Processor**: Large-scale document analysis capabilities
- **Template Report Generator**: Standardized institutional report generation
- **API Key Management**: Intelligent rotation system with 115+ Gemini API keys

**Frontend Infrastructure**
- **Professional Workbench Interface**: Institutional-grade user experience
- **Real-time Data Components**: Interactive financial visualization
- **Streaming Analysis Display**: Live content delivery with source attribution
- **Professional Styling**: Robeco brand-compliant design system

**AI Agent Framework**
- **Base Agent Architecture**: Extensible agent foundation with performance tracking
- **Streaming Professional Analysts**: Real-time analysis delivery
- **Investment Analyst Team**: Coordinated multi-specialist analysis

### Technology Stack

**Backend Technologies**
```
FastAPI 0.100.0+          - High-performance API framework
WebSockets 11.0+           - Real-time bidirectional communication  
Google Generative AI 0.3.0+ - Gemini 2.5 Flash integration
yfinance 0.2.18+           - Financial data acquisition
aiohttp 3.8.0+             - Asynchronous HTTP client
```

**Frontend Technologies**
```
HTML5/CSS3                 - Modern responsive design
Vanilla JavaScript         - Real-time WebSocket integration
Professional CSS Grid      - Data visualization components
Robeco Brand Guidelines    - Institutional styling standards
```

**System Dependencies**
```
Python 3.8+                - Runtime environment
uvicorn[standard]          - ASGI server
numpy/pandas               - Data processing
python-multipart           - File upload support
```

## Available AI Analysts

### Core Analysis Specialists

The system provides 12 specialized AI analysts, each with institutional-grade prompts and hedge fund-quality analysis capabilities:

**1. Fundamental Analysis Specialist**
- **Role**: Advanced Fundamental Analysis with 20+ years hedge fund experience
- **Focus Areas**: Financial statement analysis, business model evaluation, management assessment, capital allocation efficiency
- **Output**: Investment thesis, financial performance analysis, growth outlook, risk factors, valuation perspective
- **Usage**: `analyst_type: "fundamentals"`

**2. Industry Analysis Specialist**
- **Role**: Senior Industry Analyst with deep sector expertise
- **Focus Areas**: Industry ecosystem mapping, competitive intelligence, regulatory environment, technology disruption
- **Output**: Sector outlook, competitive landscape, industry economics, strategic positioning
- **Usage**: `analyst_type: "industry"`

**3. Technical Analysis Specialist**
- **Role**: Senior Technical Analyst with institutional trading experience
- **Focus Areas**: Chart pattern recognition, market microstructure, momentum indicators, multi-timeframe analysis
- **Output**: Trading recommendation, key technical levels, chart patterns, volume analysis, risk management
- **Usage**: `analyst_type: "technical"`

**4. Risk Analysis Specialist**
- **Role**: Senior Risk Analyst with advanced risk management credentials
- **Focus Areas**: Systematic and idiosyncratic risk identification, stress testing, scenario analysis
- **Output**: Risk assessment summary, business/operational risks, financial/credit risk, market risk
- **Usage**: `analyst_type: "risk"`

**5. ESG Analysis Specialist**
- **Role**: Senior ESG Analyst with sustainability investment expertise
- **Focus Areas**: Material ESG factor identification, environmental compliance, social responsibility, corporate governance
- **Output**: ESG investment summary, environmental assessment, social responsibility, governance evaluation
- **Usage**: `analyst_type: "esg"`

**6. Valuation Analysis Specialist**
- **Role**: Senior Valuation Analyst with advanced financial modeling skills
- **Focus Areas**: DCF modeling, relative valuation, scenario analysis, value catalyst identification
- **Output**: Valuation summary, DCF analysis, relative valuation, scenario analysis, investment recommendation
- **Usage**: `analyst_type: "valuation"`

**7. Bull Case Analysis Specialist**
- **Role**: Senior Bull Case Analyst specializing in long investment theses
- **Focus Areas**: Upside catalyst identification, competitive advantages, market opportunities, asymmetric risk/reward
- **Output**: Bull investment thesis, upside catalysts, growth acceleration, financial upside scenarios
- **Usage**: `analyst_type: "bull"`

**8. Bear Case Analysis Specialist**
- **Role**: Senior Bear Case Analyst specializing in risk identification and short theses
- **Focus Areas**: Downside risk identification, competitive threats, structural headwinds, value trap recognition
- **Output**: Bear investment thesis, downside risks, structural headwinds, execution risks
- **Usage**: `analyst_type: "bear"`

**9. Catalysts Analysis Specialist**
- **Role**: Senior Catalysts Analyst with event-driven investment expertise
- **Focus Areas**: Event-driven catalyst identification, timeline mapping, probability assessment, impact quantification
- **Output**: Near-term catalysts (0-3 months), medium-term catalysts (3-12 months), earnings catalysts, corporate actions
- **Usage**: `analyst_type: "catalysts"`

**10. Business Drivers Analysis Specialist**
- **Role**: Senior Business Drivers Analyst with operational intelligence expertise
- **Focus Areas**: Key business driver identification, recent development analysis, operational leverage assessment
- **Output**: Key business drivers, performance trends, strategic developments, operational updates
- **Usage**: `analyst_type: "drivers"`

**11. Consensus Analysis Specialist**
- **Role**: Senior Consensus Analyst with market sentiment expertise
- **Focus Areas**: Market consensus synthesis, analyst estimates, institutional sentiment, expectation management
- **Output**: Market consensus summary, analyst estimates, recommendation distribution, sentiment assessment
- **Usage**: `analyst_type: "consensus"`

**12. Anti-Consensus Analysis Specialist**
- **Role**: Senior Anti-Consensus Analyst with contrarian investment expertise
- **Focus Areas**: Contrarian thesis development, market inefficiency identification, consensus error analysis
- **Output**: Contrarian investment thesis, consensus errors, overlooked factors, alternative scenarios
- **Usage**: `analyst_type: "anti_consensus"`

## Deployment Architecture

### Production Deployment

**Primary Server Launch**
```bash
# Production launch (recommended)
python run_professional_system.py

# Direct server launch  
python src/robeco/backend/professional_streaming_server.py
```

**Network Configuration**
- **Local Access**: http://127.0.0.1:8005
- **Network Access**: http://172.20.10.2:8005 
- **Alternative Network**: http://10.14.0.2:8005
- **Auto Port Selection**: 8005-8007 range with conflict resolution

### API Endpoints

**Core Services**
```
GET  /                     - Professional workbench interface
GET  /health               - System health and capabilities
GET  /api/status           - Detailed system status
GET  /api/stock/{ticker}   - Real-time financial data
WebSocket /ws/professional - WebSocket streaming endpoint
```

## User Workflow

### Single Analyst Analysis Workflow

**Step 1: Access the Platform**
1. Navigate to http://127.0.0.1:8005 (or network URL)
2. The professional workbench interface loads automatically

**Step 2: Configure Analysis**
1. Enter **Company Name** (e.g., "Apple Inc.")
2. Enter **Ticker Symbol** (e.g., "AAPL")  
3. Select **Analyst Type** from dropdown (fundamentals, industry, technical, risk, esg, valuation, etc.)
4. Optionally add **Custom Query** for specific focus

**Step 3: Start Analysis**
1. Click "Start Analysis" button
2. WebSocket connection established automatically
3. Real-time streaming begins immediately

**Step 4: Real-time Analysis Stream**
The system streams analysis in real-time:
- **Status Updates**: Phase-by-phase progress tracking
- **Google Research**: Live source discovery and verification
- **AI Content**: Token-by-token analysis streaming
- **Citations**: Professional citation placement with [1], [2], [3] format
- **Sources**: Clickable research sources with credibility scores

**Step 5: Post-Analysis Interaction**
- **Chat with Analyst**: Ask follow-up questions to the AI analyst
- **Export Analysis**: Download results in JSON format
- **Source Verification**: Click through to original sources

**Cross-Agent Intelligence Sharing**
- Each agent builds upon previous agents' insights
- Shared intelligence context improves analysis quality
- Comprehensive synthesis of all analytical perspectives

### Bulk File Analysis Workflow

**Step 1: File Upload**
1. Select "Bulk Analysis" mode
2. Upload multiple files (PDF, DOCX, TXT supported)
3. Specify company ticker for context

**Step 2: File Processing**
- Files uploaded to Google Gemini API
- Real-time processing status updates
- Validation and format checking

**Step 3: AI Analysis**
- Comprehensive document analysis
- Integration with company research
- Source attribution and citation


**Real-time Response Types**
```javascript
streaming_analysis_started    - Analysis initiation
streaming_status_update      - Progress updates
streaming_research_source    - Source discovery
streaming_ai_content        - Token-by-token content
streaming_ai_content_final  - Complete analysis with citations
agent_deployed             - Agent initialization
agent_completed            - Agent completion metrics
streaming_analysis_completed - Final summary
```

### Chat Functionality

**Post-Analysis Chat**
```javascript
{
  "type": "chat_message",
  "data": {
    "analyst": "fundamentals",
    "message": "What are the key risks to this investment thesis?",
    "company": "AAPL",
    "ticker": "AAPL"
  }
}
```

### Professional Investment Report Generation Workflow

**Overview**
The system provides automated generation of professional investment reports using the Robeco Investment Case Template. After completing multiple analyst analyses, users can generate comprehensive HTML reports that combine all analyst insights into a professionally formatted document.

**Step 1: Complete Analyst Analyses**
1. Run multiple specialist analyses (fundamentals, industry, technical, risk, esg, valuation, etc.)
2. Each analysis is automatically saved to the persistence system
3. Minimum 2-3 analyses recommended for comprehensive reports

**Step 2: Initiate Report Generation**
1. Click the **"Generate Professional Report"** button in the specialist analysis section
2. The system validates that analyses exist for the current ticker
3. Report generation request sent via WebSocket with all stored analyses

**Step 3: Template-Based Report Generation Process**
The system follows this sophisticated workflow:

1. **Analysis Collection**: Retrieves all stored analyses for the ticker from `analysis_persistence.js`
2. **Template Loading**: Loads the professional template from `Report Example/Robeco_InvestmentCase_Template.txt`
3. **CSS Integration**: Applies fixed CSS styling from `Report Example/CSScode.txt` 
4. **AI Content Generation**: Uses Gemini AI to generate slide content based on:
   - All analyst outputs (fundamentals, industry, technical, risk, esg, valuation, bull, bear, catalysts, drivers, consensus, anti_consensus)
   - Professional Robeco template structure
   - Institutional-grade investment terminology
5. **HTML Assembly**: Combines CSS header + AI-generated slides + JavaScript footer

**Step 4: Report Output & Display**
1. **Raw HTML Code**: Complete HTML source displayed in code viewer for technical review
2. **Rendered Report**: Fully formatted report displayed in embedded viewer
3. **Local Storage**: Report automatically saved to browser storage for persistence
4. **Professional Formatting**: Multi-slide presentation with Robeco branding, metrics grids, analysis sections

**Report Structure Generated**
- **Cover Slide**: Company overview, key metrics, investment recommendation
- **Executive Summary**: Investment highlights, key thesis points
- **Financial Analysis**: Based on fundamentals analyst output
- **Industry Analysis**: Market positioning, competitive dynamics  
- **Technical Analysis**: Price trends, technical indicators
- **Risk Assessment**: Comprehensive risk evaluation
- **ESG Analysis**: Sustainability and governance factors
- **Valuation Analysis**: DCF modeling, target price, recommendation
- **Bull/Bear Cases**: Upside and downside scenarios
- **Catalysts**: Near-term and medium-term value drivers

**Key Technical Components**

**Template Report Generator (`template_report_generator.py`)**
- **Primary Function**: `generate_report_from_analyses()` - Main report generation orchestrator
- **Template Integration**: Loads `Robeco_InvestmentCase_Template.txt` as one-shot example
- **AI Prompt Building**: Constructs comprehensive prompts with all analyst outputs
- **CSS Separation**: Generates only HTML content, applies fixed CSS separately
- **Error Handling**: Retry logic with multiple API keys for reliability

**Frontend Report Handling (`robeco_professional_workbench_enhanced.html`)**
- **Report Generation Trigger**: `generateTemplateReport()` - Collects analyses and sends WebSocket request
- **Report Display**: `handleReportGenerationCompleted()` - Displays final HTML report
- **Analysis Persistence**: `analysis_persistence.js` - Stores all analyst outputs for report generation
- **Dual View**: Raw HTML code viewer + rendered report viewer

**WebSocket Report Messages**
```javascript
// Report generation request
{
  "type": "generate_report",
  "data": {
    "company_name": "Apple Inc.",
    "ticker": "AAPL", 
    "analyses_data": {
      "fundamentals": { "content": "...", "sources": [...], "timestamp": "..." },
      "industry": { "content": "...", "sources": [...], "timestamp": "..." },
      // ... all other analyst outputs
    },
    "report_focus": "comprehensive"
  }
}

// Report completion response  
{
  "type": "report_generation_completed",
  "data": {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "report_html": "<div class=\"presentation-container\">...</div>",
    "raw_content": "<!-- Full HTML source -->",
    "template_used": "Robeco_InvestmentCase_Template.txt",
    "analyses_count": 8,
    "content_length": 45000,
    "final_length": 52000
  }
}
```

**Report Template Architecture**
- **CSS Foundation**: Fixed professional styling from `CSScode.txt` (1620px × 2291px slides, Robeco branding)
- **Content Structure**: Multi-slide presentation format with consistent headers, footers, metrics grids
- **Data Integration**: Seamless integration of all analyst outputs into professional report sections
- **Professional Standards**: Institutional-grade formatting, typography, and visual hierarchy

## File Structure

### Backend Architecture
```
src/robeco/backend/
├── ultra_sophisticated_multi_agent_engine.py  # Core AI engine
├── professional_streaming_server.py           # Main server
├── professional_api.py                       # API endpoints
├── bulk_file_processor.py                    # File processing
├── template_report_generator.py              # Report generation
├── websocket_manager.py                      # WebSocket handling
├── main.py                                   # Alternative entry point
└── api_key/
    ├── primary_gemini_key.txt                # Primary API key
    ├── gemini_api_keys.txt                   # Backup key pool
    └── gemini_api_key.py                     # Key management
```

### Frontend Components
```
src/robeco/frontend/
├── templates/
│   ├── robeco_professional_workbench_enhanced.html  # Main interface
│   └── robeco_investment_workbench_mvp.html         # Alternative interface
└── static/
    ├── css/
    │   └── professional_data_components.css         # Professional styling
    └── js/
        ├── professional_data_components.js          # Data visualization
        └── analysis_persistence.js                  # Analysis storage
```

### Core System Components
```
src/robeco/
├── agents/
│   ├── base_agent.py                        # Agent foundation
│   ├── professional_investment_analyst.py   # Core analysts
│   └── streaming_professional_analyst.py    # Streaming analysts
├── core/
│   ├── config.py                           # System configuration
│   ├── memory.py                           # Shared memory
│   ├── models.py                           # Data models
│   └── utils.py                            # Utilities
├── data/
│   ├── data_processor.py                   # Data processing
│   ├── data_validator.py                   # Data validation
│   └── yfinance_fetcher.py                 # Financial data
└── prompts/
    └── institutional_analyst_prompts.py    # AI prompts
```

### Configuration Files
```
├── requirements.txt                         # Dependencies
├── run_professional_system.py              # Main launcher
└── Testing files/
    ├── test_citation_debug.py              # Citation testing
    ├── test_google_search.py               # Search testing
    └── test_websocket_debug.py             # WebSocket testing
```

## Configuration Management

### API Key Management

**File Locations**
```python
# Primary key
src/robeco/backend/api_key/primary_gemini_key.txt

# Backup pool  
src/robeco/backend/api_key/gemini_api_keys.txt

# Environment variables (optional)
GEMINI_API_KEY_1 through GEMINI_API_KEY_12
```

**Key Features**
- Automatic suspension of failed keys
- Intelligent rotation algorithms (115+ keys)
- Error recovery and retry logic
- Statistical usage tracking

## Advanced Features

### Google Search Integration
- Automatic grounding and source verification
- Real-time web research during analysis
- Credibility scoring and verification badges
- Citation placement using Google grounding supports

### Real-time Streaming Analysis
- Token-by-token content delivery via WebSocket
- Live Google Search integration with source attribution
- Professional citation placement with [1], [2], [3] format
- Cross-agent intelligence sharing and synthesis

### Professional Quality Standards
- Institutional-grade analysis depth (8,000-15,000 words)
- DCF modeling and scenario analysis
- Contrarian positioning and alpha identification
- Risk-adjusted return calculations

## Performance Characteristics

### System Capabilities

**Analysis Performance**
- Single agent analysis: 30-120 seconds
- Multi-agent comprehensive analysis: 3-8 minutes
- Real-time streaming latency: <200ms
- Google Search integration: 5-15 sources per analysis

**Quality Metrics**
- Analysis depth: 8,000-15,000 words per agent
- Source attribution: 15-30 citations per analysis
- Quality scoring: 0.8-1.0 institutional grade
- Confidence levels: 0.85-0.98 professional standard

## Installation & Development

### System Requirements
```bash
# Clone repository
git clone <repository-url>
cd "Robeco Reporting"

# Install dependencies
pip install -r requirements.txt

# Configure API keys
# Add primary key to src/robeco/backend/api_key/primary_gemini_key.txt
# Add backup keys to src/robeco/backend/api_key/gemini_api_keys.txt
```

### Development Server
```bash
# Standard development launch
python run_professional_system.py

# Direct uvicorn launch with reload
uvicorn src.robeco.backend.main:app --host 0.0.0.0 --port 8001 --reload

# Professional streaming server
python src/robeco/backend/professional_streaming_server.py
```

## Key Code Files & Architecture

### Primary System Launcher - `run_professional_system.py`

This is the main entry point for the entire Robeco Professional Investment Analysis Platform.

**Purpose**: 
- Launches the ultra-sophisticated multi-agent engine with 115+ API keys
- Configures network access for both local and network-wide availability
- Sets up the production environment with auto-port selection

**Key Features**:
```python
# Network Configuration
LOCAL_ACCESS = "http://127.0.0.1:8005"
NETWORK_ACCESS = "http://172.20.10.2:8005" 
ALTERNATIVE_NETWORK = "http://10.14.0.2:8005"

# Auto Port Selection: 8005-8007 range with conflict resolution
# Intelligent retry system with 115+ API keys
# Real-time streaming analysis capability
# Post-analysis chat functionality
```

**How to Use**:
```bash
# Production launch (recommended)
python run_professional_system.py

# The system will:
# 1. Load 115+ API keys with intelligent rotation
# 2. Auto-select available port (8005, 8006, 8007, etc.)
# 3. Display local and network access URLs
# 4. Launch professional streaming server
```

**Key Components**:
- **Environment Setup**: Configures Python path and project root
- **Logging System**: Professional logging with timestamp and level information  
- **Network Detection**: Automatically detects and displays network access URLs
- **Server Launch**: Executes the professional streaming server with sophisticated engine

### Core AI Prompt System - `institutional_analyst_prompts.py`

This file contains the sophisticated AI prompts that power all 12 specialist analysts, designed for hedge fund-quality institutional analysis.

**Architecture**:
```python
class InstitutionalAnalystPrompts:
    # 12 specialized analyst prompt methods
    @staticmethod
    def get_fundamentals_prompt(company, ticker, user_query, financial_data)
    @staticmethod 
    def get_industry_prompt(company, ticker, user_query, financial_data)
    # ... and 10 more specialist prompts
```

**Analyst Prompt Structure**:
Each analyst prompt includes:
- **Context**: 20+ years hedge fund experience background
- **Objective**: Specific analysis goals and depth requirements
- **Skills**: Technical expertise and analytical capabilities
- **Style**: Professional investment banking writing conventions
- **Tone**: Authoritative, analytical, CIO-level reporting
- **Audience**: Chief Investment Officers and senior portfolio managers
- **Source Requirements**: Mandatory [1], [2], [3] citation format
- **Output Structure**: Specific deliverables for each analysis type

**Key Features**:
```python
# Complete yfinance data integration
financial_data_integration = {
    "raw_yfinance_dataset": "Complete unfiltered access",
    "data_points": "All available metrics, ratios, indicators",
    "real_time_data": "Current prices, market cap, financial ratios"
}

# Professional writing standards
writing_standards = {
    "pyramid_structure": "Key insights first, supporting details follow",
    "banker_conventions": "Metrics in parentheses, professional terminology",
    "citation_requirements": "[1], [2], [3] format for all claims",
    "institutional_quality": "CIO-level reporting standards"
}
```

**Analyst Specializations**:

1. **Fundamentals**: Financial statement analysis, business model evaluation, capital allocation
2. **Industry**: Sector intelligence, competitive dynamics, regulatory environment
3. **Technical**: Chart patterns, market microstructure, trading strategies
4. **Risk**: Systematic/idiosyncratic risk, stress testing, scenario analysis
5. **ESG**: Environmental, social, governance factors, sustainability strategy
6. **Valuation**: DCF modeling, relative valuation, price target determination
7. **Bull Case**: Upside catalysts, competitive advantages, growth scenarios
8. **Bear Case**: Downside risks, structural headwinds, value trap identification
9. **Catalysts**: Event-driven opportunities, timeline mapping, impact quantification
10. **Drivers**: Key business drivers, operational intelligence, performance trends
11. **Consensus**: Market sentiment, analyst estimates, institutional positioning
12. **Anti-Consensus**: Contrarian opportunities, market inefficiencies, alpha generation

### Ultra-Sophisticated Multi-Agent Engine - `ultra_sophisticated_multi_agent_engine.py`

The core AI intelligence system that orchestrates sequential agent deployment with cross-agent synthesis.

**Key Classes**:
```python
class UltraSophisticatedMultiAgentEngine:
    # Strategic deployment sequence for maximum intelligence
    agent_sequence = [
        'industry',      # Market foundation and sector context
        'fundamentals',  # Financial analysis with industry context
        'technical',     # Price action with fundamental backdrop
        'risk',          # Risk assessment with full context
        'esg',           # Sustainability factors
        'valuation'      # Synthesis valuation with all insights
    ]
```

**Core Capabilities**:
- **Single Agent Analysis**: Individual specialist analysis with Google Search integration
- **Multi-Agent Sequential Analysis**: All 6 core agents with intelligence sharing
- **Real-time Streaming**: Token-by-token content delivery via WebSocket
- **Google Search Integration**: Live web research with citation placement
- **Cross-Agent Intelligence**: Each agent builds upon previous insights

### Professional Streaming Server - `professional_streaming_server.py`

The main FastAPI server that handles real-time WebSocket communication and serves the professional workbench interface.

**Key Features**:
```python
# FastAPI Application
app = FastAPI(
    title="Robeco Ultra-Sophisticated Professional Streaming Server",
    description="Sequential Intelligence Multi-Agent Architecture",
    version="2.0.0"
)

# WebSocket endpoint
@app.websocket("/ws/professional")
async def websocket_endpoint(websocket: WebSocket)

# Main interface
@app.get("/", response_class=HTMLResponse)
async def serve_workbench()
```

**Core Endpoints**:
- **`/`**: Professional workbench interface
- **`/health`**: System health and capabilities
- **`/api/status`**: Detailed system metrics
- **`/api/stock/{ticker}`**: Real-time financial data
- **`/ws/professional`**: WebSocket streaming analysis

## How to Run the Project

### Method 1: Production Launch (Recommended)

**Step 1: System Setup**
```bash
# Navigate to project directory
cd "/Users/skl/Desktop/Robeco Reporting"

# Ensure Python environment
python --version  # Should be 3.8+

# Install dependencies if not already done
pip install -r requirements.txt
```

**Step 2: API Key Configuration**
```bash
# Ensure API keys are configured
# Primary key: src/robeco/backend/api_key/primary_gemini_key.txt
# Backup keys: src/robeco/backend/api_key/gemini_api_keys.txt

# The system expects 115+ Gemini API keys for production use
```

**Step 3: Launch Production System**
```bash
# Launch the complete professional system
python run_professional_system.py
```

**Expected Output**:
```
2025-01-XX XX:XX:XX,XXX - INFO - 🚀 Starting Robeco Professional System - SOPHISTICATED ENGINE
2025-01-XX XX:XX:XX,XXX - INFO - ✅ 115+ API Keys with intelligent retry system
2025-01-XX XX:XX:XX,XXX - INFO - ✅ Real-time streaming analysis
2025-01-XX XX:XX:XX,XXX - INFO - ✅ Post-analysis chat functionality
2025-01-XX XX:XX:XX,XXX - INFO - ✅ Professional Robeco UI design
2025-01-XX XX:XX:XX,XXX - INFO - 📊 Local access: http://127.0.0.1:8005/
2025-01-XX XX:XX:XX,XXX - INFO - 🌐 Public access: http://172.20.10.2:8005/
```

**Step 4: Access the Platform**
- **Local Access**: http://127.0.0.1:8005 (or assigned port)
- **Network Access**: http://172.20.10.2:8005 (accessible from other devices)
- **Alternative**: http://10.14.0.2:8005 (different network segment)

### Method 2: Direct Server Launch

```bash
# Launch professional streaming server directly
python src/robeco/backend/professional_streaming_server.py
```

### Method 3: Development Mode with Auto-Reload

```bash
# Launch with uvicorn for development
uvicorn src.robeco.backend.main:app --host 0.0.0.0 --port 8001 --reload
```

## Production Deployment Verification

### System Health Checks

**1. Verify Server Startup**
```bash
# Check if server is running
curl http://127.0.0.1:8005/health

# Expected response:
{
  "status": "healthy",
  "multi_agent_engine": true,
  "streaming_server": true,
  "api_keys_loaded": 115+,
  "capabilities": ["real_time_analysis", "professional_reports"]
}
```

**2. Verify API Key Loading**
```bash
# Check system status
curl http://127.0.0.1:8005/api/status

# Should show:
{
  "server_info": {
    "name": "Robeco Professional Streaming Server",
    "version": "1.0.0"
  },
  "capabilities": {
    "analysis_types": [
      "fundamentals", "industry", "technical", "risk", 
      "esg", "valuation", "bull", "bear", "catalysts", 
      "drivers", "consensus", "anti_consensus"
    ]
  }
}
```

**3. Test WebSocket Connection**
```javascript
// Browser console test
const ws = new WebSocket('ws://127.0.0.1:8005/ws/professional');
ws.onopen = () => console.log('WebSocket connected');
ws.onmessage = (event) => console.log('Received:', JSON.parse(event.data));
```

### Troubleshooting Common Issues

**Port Conflicts**
```bash
# If port 8005 is busy, system auto-selects 8006, 8007, etc.
# Check logs for actual assigned port
```

**API Key Issues**
```bash
# Verify primary key exists
cat src/robeco/backend/api_key/primary_gemini_key.txt

# Verify backup keys exist
wc -l src/robeco/backend/api_key/gemini_api_keys.txt
# Should show 115+ lines
```

**WebSocket Connection Problems**
```bash
# Check firewall settings
# Ensure browser supports WebSockets
# Verify network connectivity
```