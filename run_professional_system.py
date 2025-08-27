#!/usr/bin/env python3
"""
Robeco Professional System Launcher - SOPHISTICATED ENGINE
Launches the ultra sophisticated multi-agent engine with 200+ API keys
"""

import sys
import os
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Launch the sophisticated multi-agent engine directly"""
    
    # Add project root to Python path
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path) + os.pathsep + env.get('PYTHONPATH', '')
    
    logger.info("🚀 Starting Robeco Professional System - SOPHISTICATED ENGINE")
    logger.info("✅ 115+ API Keys with intelligent retry system")
    logger.info("✅ Real-time streaming analysis")
    logger.info("✅ Post-analysis chat functionality")
    logger.info("✅ Professional Robeco UI design")
    logger.info("📊 Access at: http://127.0.0.1:8005/ (will auto-find available port if busy)")
    
    # Path to the professional streaming server (which uses the sophisticated engine)
    server_path = project_root / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    if not server_path.exists():
        logger.error(f"❌ Professional streaming server not found at: {server_path}")
        return
    
    try:
        # Launch the professional streaming server with sophisticated engine
        subprocess.run([
            sys.executable, 
            str(server_path)
        ], env=env, check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to start professional streaming server: {e}")
        logger.error("❌ Please check the server configuration and try again")
            
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()