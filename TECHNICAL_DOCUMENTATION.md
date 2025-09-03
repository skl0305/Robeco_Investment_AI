# Robeco Investment Platform - Technical Documentation

## Code Architecture & Implementation Details

This document provides comprehensive technical documentation for engineers working with the Robeco Professional Investment Analysis Platform. It covers the internal architecture, code structure, function implementations, and technical workflows.

## Core Backend Implementation

### Main System Launcher - `run_professional_system.py`

**Purpose**: Production-grade system launcher with intelligent environment configuration and network detection

**Implementation Details**:

```python
#!/usr/bin/env python3
"""
Main system launcher for Robeco Professional Investment Analysis Platform
Handles environment setup, network configuration, and server deployment
"""

def main():
    """
    Primary system initialization and launch sequence
    
    Process:
    1. Environment setup and Python path configuration
    2. Network detection and URL generation
    3. Port availability scanning (8005-8007 range)
    4. Professional streaming server launch
    5. Real-time status monitoring
    """
    
def setup_environment():
    """
    Configures Python environment and project paths
    
    Key Operations:
    - Adds project root to Python path
    - Validates Python version (3.8+ required)
    - Initializes logging system with production settings
    - Sets up working directory context
    """
    
def detect_network_urls():
    """
    Intelligent network detection and URL generation
    
    Returns:
    - Local access URL (127.0.0.1)
    - Primary network URL (172.20.10.2) 
    - Alternative network URL (10.14.0.2)
    - Auto-detected available ports
    """
    
def check_port_availability(port):
    """
    Port availability verification with socket testing
    
    Args:
        port (int): Port number to test
        
    Returns:
        bool: True if port is available
    """
```

**Network Configuration**:
```python
# Default network endpoints
LOCAL_ACCESS = "http://127.0.0.1:8005"
NETWORK_ACCESS = "http://172.20.10.2:8005"  
ALTERNATIVE_NETWORK = "http://10.14.0.2:8005"

# Port scanning range with conflict resolution
PORT_RANGE = [8005, 8006, 8007]
```

### AI Prompt System - `institutional_analyst_prompts.py`

**Purpose**: Sophisticated AI prompts delivering hedge fund-quality institutional analysis across 12 specialist areas

**Class Architecture**:

```python
class InstitutionalAnalystPrompts:
    """
    Static prompt generation for all 12 specialist analysts
    Each prompt designed for institutional-grade analysis quality
    """
    
    @staticmethod
    def get_fundamentals_prompt(company: str, ticker: str, user_query: str, financial_data: dict) -> str:
        """
        Fundamentals Analysis Specialist Prompt
        
        Context: Senior Fundamental Analyst with 20+ years hedge fund experience
        Focus: Financial statement analysis, business model evaluation, capital allocation
        Output: Investment thesis, financial performance, growth outlook, risk factors
        
        Args:
            company: Company name for analysis
            ticker: Stock ticker symbol
            user_query: Specific analysis focus
            financial_data: Complete yfinance dataset
            
        Returns:
            str: Complete prompt for fundamentals analysis
        """
        
    @staticmethod
    def get_industry_prompt(company: str, ticker: str, user_query: str, financial_data: dict) -> str:
        """
        Industry Analysis Specialist Prompt
        
        Context: Senior Industry Analyst with deep sector expertise
        Focus: Competitive dynamics, market positioning, regulatory environment
        Output: Industry overview, competitive analysis, market trends, sector outlook
        """
        
    @staticmethod
    def get_technical_prompt(company: str, ticker: str, user_query: str, financial_data: dict) -> str:
        """
        Technical Analysis Specialist Prompt
        
        Context: Senior Technical Analyst with quantitative trading background
        Focus: Chart patterns, market microstructure, trading strategies
        Output: Technical summary, price trends, momentum indicators, trading recommendations
        """
        
    # Additional 9 specialist prompts:
    # - get_risk_prompt(): Risk assessment and mitigation strategies
    # - get_esg_prompt(): Environmental, social, governance analysis
    # - get_valuation_prompt(): DCF modeling and relative valuation
    # - get_bull_prompt(): Upside catalysts and growth scenarios
    # - get_bear_prompt(): Downside risks and structural headwinds
    # - get_catalysts_prompt(): Event-driven opportunities and timeline mapping
    # - get_drivers_prompt(): Key business drivers and operational intelligence
    # - get_consensus_prompt(): Market sentiment and analyst estimates
    # - get_anti_consensus_prompt(): Contrarian opportunities and alpha generation
```

**Prompt Structure Standards**:
```python
# Each prompt follows this institutional framework:
prompt_structure = {
    "context": "20+ years hedge fund experience background",
    "skills": "Technical expertise and analytical capabilities",
    "objective": "Specific analysis goals and deliverables", 
    "style": "Investment banking writing conventions",
    "tone": "Authoritative, analytical, CIO-level reporting",
    "audience": "Chief Investment Officers and portfolio managers",
    "data_integration": "Complete yfinance dataset access",
    "citation_requirements": "[1], [2], [3] source format mandatory",
    "output_structure": "Specific deliverables for each analyst type"
}
```

### Multi-Agent Intelligence Engine - `ultra_sophisticated_multi_agent_engine.py`

**Purpose**: Core AI orchestration system managing sequential agent deployment with cross-agent intelligence synthesis

**Class Implementation**:

```python
class UltraSophisticatedMultiAgentEngine:
    """
    Ultra-sophisticated AI agent deployment and intelligence synthesis system
    Manages 12 specialist analysts with strategic deployment sequencing
    """
    
    def __init__(self):
        """
        Initialize multi-agent system
        
        Key Components:
        - Agent sequence configuration
        - Intelligence sharing protocols  
        - Cross-agent synthesis capabilities
        - Performance tracking and optimization
        """
        self.agent_sequence = [
            "fundamentals", "industry", "technical", "risk", "esg", "valuation",
            "bull", "bear", "catalysts", "drivers", "consensus", "anti_consensus"
        ]
        self.intelligence_context = {}
        self.agent_outputs = {}
        
    async def deploy_agent_sequence(self, context: AnalysisContext) -> Dict[str, Any]:
        """
        Strategic agent deployment with intelligence sharing
        
        Process:
        1. Sequential agent deployment in optimized order
        2. Intelligence context sharing between agents
        3. Progressive analysis building and refinement
        4. Cross-agent validation and synthesis
        
        Args:
            context: Analysis context with company, ticker, objectives
            
        Returns:
            Dict: Comprehensive analysis from all deployed agents
        """
        
    async def synthesize_agent_outputs(self, agent_results: Dict[str, Any]) -> str:
        """
        Cross-agent intelligence synthesis and consolidation
        
        Process:
        1. Extract key insights from each agent
        2. Identify consensus and contrarian viewpoints
        3. Synthesize comprehensive investment thesis
        4. Generate final consolidated analysis
        
        Args:
            agent_results: Dictionary of all agent analysis outputs
            
        Returns:
            str: Synthesized comprehensive analysis
        """
        
    def update_intelligence_context(self, agent_type: str, analysis_output: str):
        """
        Updates shared intelligence context for subsequent agents
        
        Args:
            agent_type: Type of analyst providing intelligence
            analysis_output: Analysis content to share with other agents
        """
```

**Agent Deployment Strategy**:
```python
# Strategic deployment sequence for maximum intelligence
deployment_strategy = {
    "phase_1": ["fundamentals", "industry"],  # Foundation analysis
    "phase_2": ["technical", "risk"],         # Market and risk assessment  
    "phase_3": ["esg", "valuation"],         # Valuation and sustainability
    "phase_4": ["bull", "bear"],             # Scenario analysis
    "phase_5": ["catalysts", "drivers"],     # Catalyst identification
    "phase_6": ["consensus", "anti_consensus"] # Market positioning
}
```

### Professional Report Generator - `template_report_generator.py`

**Purpose**: Institutional-grade investment report generation using Robeco template structure

**Class Implementation**:

```python
class RobecoTemplateReportGenerator:
    """
    Professional investment report generator
    Combines AI content generation with fixed Robeco template structure
    """
    
    def __init__(self):
        """
        Initialize report generator with template configuration
        
        Key Setup:
        - Template path configuration to Robeco_InvestmentCase_Template.txt
        - CSS integration path to CSScode.txt
        - AI generation parameters and retry logic
        """
        self.template_path = "/Users/skl/Desktop/Robeco Reporting/Report Example/Robeco_InvestmentCase_Template.txt"
        
    async def generate_report_from_analyses(
        self, 
        company_name: str,
        ticker: str, 
        analyses_data: Dict[str, Any],
        report_focus: str = "comprehensive"
    ) -> str:
        """
        Main report generation orchestrator
        
        Process:
        1. Load Robeco template as structural example
        2. Build comprehensive AI prompt with all analyst outputs
        3. Generate slide content using Gemini 2.0 Flash
        4. Combine fixed CSS with AI-generated content
        5. Produce final professional HTML report
        
        Args:
            company_name: Company name for report header
            ticker: Stock ticker symbol
            analyses_data: Dictionary of all completed analyst outputs
            report_focus: Report type (comprehensive, focused, etc.)
            
        Returns:
            str: Complete HTML report with CSS, content, and JavaScript
        """
        
    async def _build_report_generation_prompt(
        self, 
        company_name: str, 
        ticker: str, 
        analyses_data: Dict[str, Any]
    ) -> str:
        """
        Constructs comprehensive AI prompt for report generation
        
        Prompt Components:
        1. Template structure example from Robeco_InvestmentCase_Template.txt
        2. All 12 analyst outputs with full content and sources
        3. Professional formatting requirements
        4. CSS class specifications
        5. Institutional writing standards
        
        Returns:
            str: Complete prompt for AI report generation
        """
        
    async def _generate_ai_report(self, prompt: str) -> str:
        """
        AI content generation with production-grade reliability
        
        Features:
        - Gemini 2.0 Flash model with 65,536 token limit
        - Streaming response handling for large content
        - Automatic API key rotation on failures
        - Retry logic with exponential backoff
        - Content validation and error recovery
        
        Args:
            prompt: Complete report generation prompt
            
        Returns:
            str: AI-generated slide content (HTML only, no CSS)
        """
        
    def _combine_css_with_slides(self, company_name: str, ticker: str, slides_content: str) -> str:
        """
        Combines fixed CSS styling with AI-generated slide content
        
        Process:
        1. Load fixed CSS header with Robeco branding
        2. Clean AI-generated content (remove any CSS/HTML headers)
        3. Extract presentation-container div content
        4. Combine CSS + slides + JavaScript footer
        5. Validate final HTML structure
        
        Returns:
            str: Complete professional HTML report
        """
```

**AI Generation Configuration**:
```python
# Gemini API configuration for report generation
generate_config = types.GenerateContentConfig(
    temperature=0.1,        # Low for consistent, professional output
    top_p=0.85,            # Focused sampling for institutional quality
    max_output_tokens=65536, # Maximum tokens for complete analysis
    response_mime_type="text/plain",
    system_instruction="Senior institutional investment analyst generating professional investment slides"
)
```

### WebSocket Streaming Server - `professional_streaming_server.py`

**Purpose**: FastAPI server with WebSocket streaming for real-time analysis delivery and report generation

**Key Functions**:

```python
@app.websocket("/ws/professional")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time analysis streaming
    
    Handles:
    - Connection establishment and authentication
    - Message routing to appropriate handlers
    - Real-time content streaming
    - Error handling and connection recovery
    """
    
async def handle_analysis_request(websocket: WebSocket, connection_id: str, message: Dict):
    """
    Processes analysis requests and coordinates agent deployment
    
    Process:
    1. Extract analysis parameters (company, ticker, analyst_type)
    2. Validate input data and check API key availability
    3. Deploy appropriate specialist agent
    4. Stream real-time analysis content
    5. Handle citations and source integration
    6. Send completion notifications
    
    WebSocket Messages Sent:
    - streaming_analysis_started
    - streaming_status_update
    - streaming_research_source
    - streaming_ai_content
    - streaming_ai_content_final
    - streaming_analysis_completed
    """
    
async def handle_report_generation(websocket: WebSocket, connection_id: str, message: Dict):
    """
    Orchestrates comprehensive report generation workflow
    
    Process:
    1. Extract report parameters and validate analyses_data
    2. Load Robeco template from Report Example/Robeco_InvestmentCase_Template.txt
    3. Build comprehensive prompt with all analyst outputs
    4. Generate report content using template_report_generator
    5. Stream progress updates to frontend
    6. Send final HTML report to client
    
    WebSocket Messages Sent:
    - report_generation_started
    - streaming_ai_content (progress updates)
    - report_generation_completed
    """
    
async def handle_bulk_analysis_streaming(websocket: WebSocket, connection_id: str, message: Dict):
    """
    Manages bulk file analysis with streaming progress updates
    
    Features:
    - Multi-file upload processing
    - Real-time progress tracking
    - Chunked content delivery
    - Error handling for large files
    """
```

**WebSocket Message Protocol**:
```python
# Message routing system
message_handlers = {
    "start_analysis": handle_analysis_request,
    "generate_report": handle_report_generation,
    "bulk_analysis": handle_bulk_analysis_streaming,
    "chat_message": handle_chat_request,
    "file_upload": handle_file_upload
}

# Connection management
active_connections = {}  # {connection_id: WebSocket}
connection_metadata = {}  # {connection_id: metadata}
```

### API Key Management - `gemini_api_key.py`

**Purpose**: Intelligent API key rotation and management system

**Implementation**:
```python
def get_intelligent_api_key(agent_type: str = "general") -> Tuple[str, dict]:
    """
    Intelligent API key selection with rotation and fallback
    
    Process:
    1. Check primary key availability
    2. Rotate through backup key pool (115+ keys)
    3. Track key usage and suspension status
    4. Implement exponential backoff on failures
    5. Log key rotation events for monitoring
    
    Args:
        agent_type: Type of agent requesting key (for usage tracking)
        
    Returns:
        Tuple[str, dict]: (api_key, key_metadata)
    """
    
def load_api_keys() -> List[str]:
    """
    Loads API keys from multiple sources
    
    Sources:
    1. primary_gemini_key.txt (primary key)
    2. gemini_api_keys.txt (backup pool)
    3. Environment variables (GEMINI_API_KEY_1 through GEMINI_API_KEY_12)
    
    Returns:
        List[str]: All available API keys
    """
```

## Frontend Implementation

### Main User Interface - `robeco_professional_workbench_enhanced.html`

**Purpose**: Professional workbench interface with real-time streaming, analysis management, and report generation

**Key JavaScript Functions**:

```javascript
// ========================================
// PROJECT SETUP AND CONFIGURATION
// ========================================

function setupInvestmentProject() {
    /**
     * Initializes investment project with validation
     * 
     * Process:
     * 1. Extract company name and ticker from input fields
     * 2. Validate input format and requirements
     * 3. Configure currentProject global object
     * 4. Navigate to specialist analysis phase
     * 5. Initialize analyst status tracking
     */
}

function navigateToPhase(phase) {
    /**
     * Phase navigation with state management
     * 
     * Phases:
     * - 'project-setup': Initial configuration
     * - 'specialist-analysis': Analyst selection and execution
     * - 'report-generation': Professional report creation
     */
}

// ========================================
// ANALYST MANAGEMENT AND EXECUTION
// ========================================

function handleAnalystClick(analystType) {
    /**
     * Specialist analyst selection and analysis initiation
     * 
     * Process:
     * 1. Validate project setup and WebSocket connection
     * 2. Check for cached analysis results
     * 3. Update UI to show selected analyst
     * 4. Initiate analysis or display cached results
     * 
     * Args:
     *     analystType: One of 12 specialist types (fundamentals, industry, etc.)
     */
}

function startSpecialistAnalysis(analystType) {
    /**
     * Initiates real-time streaming analysis
     * 
     * WebSocket Message Sent:
     * {
     *   "type": "start_analysis",
     *   "data": {
     *     "company": currentProject.company,
     *     "ticker": currentProject.ticker,
     *     "analyst_type": analystType,
     *     "user_query": customQuery || ""
     *   }
     * }
     */
}

// ========================================
// REAL-TIME STREAMING HANDLERS
// ========================================

function handleStreamingContent(data) {
    /**
     * Processes real-time streaming analysis content
     * 
     * Features:
     * - Token-by-token content streaming
     * - Citation processing and link generation
     * - Source integration and display
     * - Progress tracking and status updates
     */
}

function handleFinalContentWithCitations(data) {
    /**
     * Processes final analysis with complete citation integration
     * 
     * Process:
     * 1. Replace streaming content with final version
     * 2. Process and format citations [1], [2], [3]
     * 3. Generate clickable citation links
     * 4. Display research sources with credibility scores
     * 5. Save to analysis persistence system
     */
}

// ========================================
// REPORT GENERATION SYSTEM
// ========================================

function generateTemplateReport() {
    /**
     * Initiates professional report generation workflow
     * 
     * Process:
     * 1. Validate current project setup
     * 2. Collect all stored analyses using robecoAnalysisPersistence
     * 3. Organize analyses by agent type
     * 4. Send WebSocket report generation request
     * 5. Display generation progress to user
     * 
     * WebSocket Message:
     * {
     *   "type": "generate_report",
     *   "data": {
     *     "company_name": currentProject.company,
     *     "ticker": currentProject.ticker,
     *     "analyses_data": {
     *       "fundamentals": { content, sources, timestamp },
     *       "industry": { content, sources, timestamp },
     *       // ... all other completed analyses
     *     },
     *     "report_focus": "comprehensive"
     *   }
     * }
     */
}

function handleReportGenerationCompleted(data) {
    /**
     * Handles completed report generation and display
     * 
     * Process:
     * 1. Display raw HTML code in code viewer
     * 2. Render final report in embedded viewer
     * 3. Save report to localStorage for persistence
     * 4. Show success notification with report details
     * 
     * Data Received:
     * - report_html: Complete formatted report
     * - raw_content: Full HTML source code
     * - analyses_count: Number of analyses included
     * - template_used: Template file used for generation
     */
}
```

**UI State Management**:
```javascript
// Global state variables
let currentProject = null;          // Current company/ticker being analyzed
let currentAnalysis = null;         // Currently selected analyst type
let currentAnalystType = null;      // Active analyst for streaming
let analysisCache = {};            // Cached analysis results
let ws = null;                     // WebSocket connection
let isGeneratingReport = false;    // Report generation state
```

### Analysis Persistence System - `analysis_persistence.js`

**Purpose**: Persistent storage and retrieval system for analysis results, enabling report generation and historical review

**Class Implementation**:

```javascript
class RobecoAnalysisPersistence {
    /**
     * Analysis persistence and retrieval system
     * Manages localStorage-based storage for all analysis results
     */
    
    constructor() {
        /**
         * Initialize persistence system
         * 
         * Setup:
         * - Storage key configuration
         * - Session ID generation  
         * - Analysis history UI setup
         */
        this.storageKey = 'robeco_professional_analyses';
        this.currentSession = this.generateSessionId();
    }
    
    saveAnalysis(analysisData) {
        /**
         * Saves completed analysis to localStorage
         * 
         * Storage Structure:
         * {
         *   id: "analysis_timestamp",
         *   sessionId: "session_id", 
         *   timestamp: "ISO_timestamp",
         *   company: "Company Name",
         *   ticker: "TICKER",
         *   analystType: "fundamentals|industry|technical|...",
         *   content: "Full HTML analysis content",
         *   sources: [{title, url, credibility_score}],
         *   qualityScore: 0.95,
         *   processingTime: 45.2,
         *   status: "completed"
         * }
         * 
         * Args:
         *     analysisData: Complete analysis data object
         * 
         * Returns:
         *     str: Unique analysis ID for retrieval
         */
    }
    
    getAnalysesByTicker(ticker) {
        /**
         * Retrieves all analyses for a specific ticker
         * Essential for report generation workflow
         * 
         * Args:
         *     ticker: Stock ticker symbol
         *     
         * Returns:
         *     Array: All analysis records for the ticker
         */
    }
    
    loadAnalysis(analysisId) {
        /**
         * Loads historical analysis and restores UI state
         * 
         * Process:
         * 1. Retrieve analysis from localStorage
         * 2. Populate project form with company/ticker
         * 3. Navigate to specialist analysis phase
         * 4. Display analysis content and sources
         * 5. Show completion state
         */
    }
}
```

### Data Visualization System - `professional_data_components.js`

**Purpose**: Professional data visualization and traceability components for financial analysis

**Class Implementation**:

```javascript
class RobecoDataManager {
    /**
     * Professional data visualization and management system
     * Provides institutional-grade data display and traceability
     */
    
    constructor() {
        /**
         * Initialize data management system
         * 
         * Components:
         * - Data cache for performance
         * - Quality monitoring system
         * - Data lineage tracking
         * - Export capabilities
         */
        this.dataCache = new Map();
        this.dataQuality = new Map();
        this.dataLineage = new Map();
    }
    
    createFinancialMetricsGrid(data, containerId) {
        /**
         * Creates professional financial metrics visualization
         * 
         * Features:
         * - Real-time metric cards with change indicators
         * - Data quality indicators
         * - Source attribution and timestamps
         * - Interactive metric details
         * 
         * Metrics Displayed:
         * - Market Cap, P/E Ratio, ROE, Debt/Equity
         * - Free Cash Flow, Revenue Growth
         * - Quality scores and data lineage
         */
    }
    
    createProfessionalDataTable(data, config, containerId) {
        /**
         * Generates professional data tables with export capabilities
         * 
         * Features:
         * - Sortable columns with professional styling
         * - Export to CSV, Excel, JSON formats
         * - Real-time filtering and search
         * - Data quality indicators
         * - Source traceability
         */
    }
}
```

## Report Template Architecture

### Template Structure - `Robeco_InvestmentCase_Template.txt`

**Purpose**: Complete HTML template defining professional investment report structure and formatting

**Template Components**:

```html
<!-- CSS Variables and Robeco Branding -->
:root {
    --robeco-blue: #005F90;
    --robeco-blue-darker: #003D5A; 
    --robeco-brown-black: #3B312A;
    --robeco-orange: #FF8C00;
    /* Professional color palette */
}

<!-- Slide Layout System -->
.slide {
    width: 1620px;           /* Professional presentation width */
    height: 2291px;          /* A4 aspect ratio for print compatibility */
    padding: 105px 98px;     /* Institutional margin standards */
    /* Multi-slide presentation format */
}

<!-- Financial Metrics Grid -->
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);  /* 4-column layout */
    /* Professional financial data display */
}

<!-- Analysis Content Structure -->
.analysis-item {
    display: flex;
    /* Structured analysis sections with consistent formatting */
}
```

**Slide Structure**:
1. **Cover Slide**: Company overview, key metrics, investment recommendation
2. **Executive Summary**: Investment highlights and fundamental conclusion
3. **Financial Performance**: Income statement, balance sheet, cash flow analysis  
4. **Industry Analysis**: Market dynamics and competitive positioning
5. **Technical Analysis**: Price trends and technical indicators
6. **Risk Assessment**: Comprehensive risk evaluation
7. **ESG Analysis**: Environmental, social, governance factors
8. **Valuation Analysis**: DCF modeling and target price derivation
9. **Bull/Bear Cases**: Upside and downside scenarios
10. **Catalysts**: Near-term and medium-term value drivers

### CSS Styling System - `CSScode.txt`

**Purpose**: Fixed professional styling providing consistent Robeco branding and institutional-grade visual presentation

**Key Style Categories**:

```css
/* Professional Typography */
.report-title { font-size: 57px; font-weight: 700; }
.report-subtitle { font-size: 27px; color: var(--text-dark); }
.section-title { 
    font-size: 25.5px; 
    border-bottom: 5px solid var(--robeco-blue);
    /* Professional section headers */
}

/* Financial Data Display */
.metrics-grid {
    /* 4-column responsive grid for financial metrics */
    border-top: 5px solid var(--robeco-blue);
    border-bottom: 5px solid var(--robeco-blue);
}

.compact-table {
    /* Professional financial data tables */
    border-collapse: collapse;
    font-size: 18px;
}

/* Analysis Content Layout */
.analysis-item {
    /* Structured analysis sections */
    border-bottom: 3.5px solid var(--robeco-blue);
    display: flex;
}

/* Professional Branding */
.robeco-logo-container {
    /* Consistent logo placement and sizing */
    position: absolute;
    top: -75px;
    right: 0;
}
```

## Data Processing and Integration

### Financial Data Integration - `yfinance_fetcher.py`

**Purpose**: Real-time financial data retrieval and processing for analysis integration

**Implementation**:
```python
class YFinanceFetcher:
    """
    Professional financial data acquisition system
    Integrates with yfinance for real-time market data
    """
    
    async def fetch_company_data(self, ticker: str) -> Dict[str, Any]:
        """
        Comprehensive financial data retrieval
        
        Data Points Retrieved:
        - Real-time pricing and market cap
        - Financial ratios and performance metrics
        - Historical price data and volatility
        - Fundamental data and financial statements
        - Analyst estimates and consensus data
        
        Returns:
            Dict: Complete financial dataset for AI analysis
        """
        
    def calculate_financial_metrics(self, raw_data: Dict) -> Dict[str, float]:
        """
        Advanced financial metrics calculation
        
        Calculated Metrics:
        - Valuation ratios (P/E, EV/EBITDA, P/B)
        - Profitability metrics (ROE, ROA, ROIC)
        - Leverage ratios (Debt/Equity, Net Debt/EBITDA)
        - Efficiency metrics (Asset turnover, Working capital)
        - Growth rates (Revenue, Earnings, FCF)
        """
```

### Configuration Management - `config.py`

**Purpose**: Centralized system configuration with environment-specific settings

**Configuration Classes**:
```python
class SystemConfig:
    """
    Core system configuration management
    """
    
    # Server Configuration
    HOST = "0.0.0.0"
    PORT_RANGE = [8005, 8006, 8007]
    WEBSOCKET_TIMEOUT = 300
    
    # AI Configuration  
    MAX_TOKENS = 65536
    TEMPERATURE = 0.1
    TOP_P = 0.85
    RETRY_ATTEMPTS = 3
    
    # File Paths
    TEMPLATE_PATH = "Report Example/Robeco_InvestmentCase_Template.txt"
    CSS_PATH = "Report Example/CSScode.txt"
    API_KEY_PATH = "src/robeco/backend/api_key/"
    
class AnalysisConfig:
    """
    Analysis-specific configuration
    """
    
    # Analyst Types
    AVAILABLE_ANALYSTS = [
        "fundamentals", "industry", "technical", "risk", "esg", "valuation",
        "bull", "bear", "catalysts", "drivers", "consensus", "anti_consensus"
    ]
    
    # Analysis Parameters
    DEFAULT_ANALYSIS_DEPTH = "comprehensive"
    CITATION_FORMAT = "[1], [2], [3]"
    SOURCE_CREDIBILITY_THRESHOLD = 0.7
```

## Error Handling and Monitoring

### Backend Error Management

**API Key Rotation System**:
```python
# Automatic failover on API key suspension
try:
    response = await gemini_client.generate_content(prompt)
except Exception as e:
    if "suspended" in str(e).lower() or "403" in str(e):
        logger.info(f"🔄 Key suspended, rotating: {api_key[:8]}...")
        new_key = get_next_available_key()
        retry_with_new_key(new_key)
```

**WebSocket Error Recovery**:
```python
# Connection management and recovery
try:
    await websocket.send_text(json.dumps(message))
except WebSocketDisconnect:
    logger.warning(f"🔌 WebSocket disconnected: {connection_id}")
    cleanup_connection(connection_id)
except Exception as e:
    logger.error(f"❌ WebSocket error: {e}")
    await send_error_message(websocket, str(e))
```

### Frontend Error Handling

**WebSocket Connection Management**:
```javascript
// Automatic reconnection logic
ws.onerror = function(error) {
    console.error('❌ WebSocket error:', error);
    showUserDebugError('Connection Error', 'WebSocket connection failed');
    
    // Attempt reconnection after delay
    setTimeout(() => {
        initWebSocket();
    }, 5000);
};

// Analysis error display
function handleAnalysisError(data) {
    updateAnalystStatus(currentAnalysis, 'error', 'Failed');
    showUserDebugError('Analysis Failed', data.error, [
        'Check API key availability',
        'Verify network connection',
        'Try refreshing page and running analysis again'
    ]);
}
```

**User Notification System**:
```javascript
function showUserDebugError(title, message, suggestions = []) {
    /**
     * Professional error display with actionable suggestions
     * 
     * Features:
     * - Clear error categorization
     * - Actionable troubleshooting steps
     * - Professional styling and positioning
     * - Auto-dismiss with manual override
     */
}

function showUserDebugSuccess(title, message) {
    /**
     * Success notification system
     * Provides positive feedback for completed operations
     */
}
```

## Testing and Validation

### Test Files Structure

```python
# Testing files/
├── test_citation_debug.py       # Citation processing validation
├── test_google_search.py        # Search integration testing  
└── test_websocket_debug.py      # WebSocket functionality testing
```

**Citation Testing**:
```python
# test_citation_debug.py
def test_citation_processing():
    """
    Validates citation generation and formatting
    Tests [1], [2], [3] format consistency
    """
    
def test_source_integration():
    """
    Validates research source integration
    Tests credibility scoring and URL validation
    """
```

**WebSocket Testing**:
```python
# test_websocket_debug.py  
def test_connection_stability():
    """
    Tests WebSocket connection reliability
    Validates message delivery and error recovery
    """
    
def test_streaming_performance():
    """
    Tests real-time streaming performance
    Validates content delivery speed and accuracy
    """
```

## Performance Optimization

### Backend Performance Features

**API Key Pool Management**:
- **115+ API Keys**: Extensive backup pool for high-volume analysis
- **Intelligent Rotation**: Automatic failover on key suspension
- **Load Balancing**: Distributes requests across available keys
- **Usage Tracking**: Monitors key performance and availability

**Streaming Optimization**:
- **Chunked Delivery**: Large content split into manageable chunks
- **Progressive Loading**: Content displayed as it generates
- **Connection Pooling**: Efficient WebSocket connection management
- **Memory Management**: Automatic cleanup of completed analyses

### Frontend Performance Features

**Caching System**:
```javascript
// Analysis caching for improved performance
const analysisCache = {};
const cacheKey = ticker + '_' + analystType;

// Check cache before requesting new analysis
if (analysisCache[cacheKey]) {
    displayCachedAnalysis(analysisCache[cacheKey]);
} else {
    startNewAnalysis(analystType);
}
```

**Lazy Loading**:
- **Content Streaming**: Progressive content display during generation
- **Source Loading**: Research sources loaded after main content
- **Image Optimization**: Lazy loading of company logos and charts
- **Memory Cleanup**: Automatic disposal of unused analysis data

## Production Deployment

### Environment Setup

**System Requirements**:
```bash
# Python Environment
Python 3.8+ (recommended: 3.11+)
pip 21.0+

# Network Configuration  
Port availability: 8005-8007 range
Network access: 172.20.10.2 or 10.14.0.2
WebSocket support required

# API Requirements
115+ Gemini API keys (recommended)
Google Search API access
YFinance data access
```

**Deployment Configuration**:
```python
# Production settings in config.py
PRODUCTION_CONFIG = {
    "host": "0.0.0.0",
    "port_range": [8005, 8006, 8007],
    "api_key_pool_size": 115,
    "max_concurrent_analyses": 50,
    "websocket_timeout": 300,
    "report_generation_timeout": 600
}
```

### Monitoring and Logging

**Backend Logging**:
```python
# Structured logging with context
logger.info(f"🚀 Analysis started: {ticker} | Agent: {analyst_type}")
logger.info(f"📊 Progress: {chunk_count} chunks, {len(content)} chars")
logger.info(f"✅ Analysis completed: {processing_time:.2f}s")
logger.error(f"❌ API error: {error} | Key: {api_key[:8]}...")
```

**Frontend Monitoring**:
```javascript
// Performance tracking
console.log('📊 Analysis metrics:', {
    processingTime: data.processing_time,
    contentLength: data.content.length,
    citationsCount: data.citations_count,
    sourcesCount: data.sources.length
});

// Error tracking with context
console.error('❌ Error context:', {
    function: 'handleAnalysisError',
    analyst: currentAnalystType,
    ticker: currentProject?.ticker,
    error: error.message
});
```