"""
Configuration settings for Robeco AI System

Centralizes all system configuration and settings management.
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class Settings:
    """System configuration settings"""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True
    
    # API settings
    GEMINI_API_KEYS: List[str] = None
    API_RATE_LIMIT: int = 60  # requests per minute
    API_TIMEOUT: int = 30  # seconds
    # DEMO_MODE removed - always use real AI
    
    # Data settings
    YFINANCE_TIMEOUT: int = 30
    CACHE_DURATION: int = 300  # 5 minutes
    MAX_HISTORY_PERIOD: str = "5y"
    
    # Agent settings
    MAX_CONCURRENT_AGENTS: int = 10
    AGENT_TIMEOUT: int = 120  # seconds
    QUALITY_THRESHOLD: float = 0.7
    
    # WebSocket settings
    WEBSOCKET_PING_INTERVAL: int = 30
    WEBSOCKET_PING_TIMEOUT: int = 10
    MAX_WEBSOCKET_CONNECTIONS: int = 100
    
    # Report settings
    REPORT_TEMPLATE_PATH: str = "src/robeco/reports/templates/robeco_template.html"
    REPORT_OUTPUT_DIR: str = "reports"
    REPORT_QUALITY_THRESHOLD: float = 0.8
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "robeco_system.log"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Security settings
    CORS_ORIGINS: List[str] = None
    RATE_LIMIT_ENABLED: bool = True
    API_KEY_ROTATION: bool = True
    
    def __post_init__(self):
        """Initialize default values and validate settings"""
        if self.GEMINI_API_KEYS is None:
            self.GEMINI_API_KEYS = self._load_api_keys()
        
        if self.CORS_ORIGINS is None:
            self.CORS_ORIGINS = [
                "http://localhost:8000",
                "http://127.0.0.1:8000",
                "http://localhost:3000"
            ]
        
        # Create necessary directories
        Path(self.REPORT_OUTPUT_DIR).mkdir(exist_ok=True)
        
    def _load_api_keys(self) -> List[str]:
        """Load API keys - primary key first, then backup pool"""
        api_keys = []
        
        # Try environment variables first
        for i in range(1, 13):
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key:
                api_keys.append(key)
        
        if not api_keys:
            try:
                # Load primary key first  
                primary_key_file = "/Users/skl/Desktop/Robeco Reporting/src/robeco/backend/api_key/primary_gemini_key.txt"
                
                if os.path.exists(primary_key_file):
                    with open(primary_key_file, 'r') as f:
                        primary_key = f.read().strip()
                        if primary_key:
                            api_keys.append(primary_key)
                            print(f"✅ Loaded primary API key: {primary_key[:8]}...")
                
                # Load backup pool
                backup_file = "/Users/skl/Desktop/Robeco Reporting/src/robeco/backend/api_key/gemini_api_keys.txt"
                
                if os.path.exists(backup_file):
                    with open(backup_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and line not in api_keys:
                                api_keys.append(line)
                    
                    print(f"✅ Total keys loaded: {len(api_keys)} (1 primary + {len(api_keys)-1} backup)")
                    
            except Exception as e:
                print(f"❌ Error loading API keys: {e}")
        
        if not api_keys:
            raise ValueError("❌ No API keys loaded from files!")
        return api_keys
    
    def get_database_url(self) -> str:
        """Get database URL (for future database integration)"""
        return os.getenv('DATABASE_URL', 'sqlite:///robeco.db')
    
    def get_redis_url(self) -> str:
        """Get Redis URL (for future caching integration)"""
        return os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'
    
    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                },
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.LOG_LEVEL,
                    'formatter': 'default',
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': self.LOG_LEVEL,
                    'formatter': 'detailed',
                    'filename': self.LOG_FILE,
                    'maxBytes': self.LOG_MAX_SIZE,
                    'backupCount': self.LOG_BACKUP_COUNT,
                },
            },
            'loggers': {
                'robeco': {
                    'level': self.LOG_LEVEL,
                    'handlers': ['console', 'file'],
                    'propagate': False,
                },
            },
        }


# Global settings instance
settings = Settings()