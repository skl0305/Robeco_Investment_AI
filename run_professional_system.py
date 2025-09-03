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
    logger.info("📊 Local access: http://127.0.0.1:8005/ (will auto-find available port if busy)")
    logger.info("🌐 Public access: http://172.20.10.2:8005/ (same port, accessible from network)")
    logger.info("🔗 Alternative: http://10.14.0.2:8005/ (if on different network segment)")
    logger.info("")
    logger.info("📋 REMINDER: Server will auto-select available port (8005, 8006, 8007, etc.)")
    logger.info("🔧 Update your public URLs accordingly when server starts")
    logger.info("🌐 Replace '8005' with actual port in your public access URLs")
    
    # Path to the professional streaming server (which uses the sophisticated engine)
    server_path = project_root / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    if not server_path.exists():
        logger.error(f"❌ Professional streaming server not found at: {server_path}")
        return
    
    try:
        # Display final public access information
        logger.info("")
        logger.info("=" * 80)
        logger.info("🌍 FINAL PUBLIC ACCESS INFORMATION")
        logger.info("=" * 80)
        logger.info("📍 Once server starts, access from ANY device on your network:")
        logger.info("🔗 Main Interface: http://172.20.10.2:[PORT]")
        logger.info("🔗 Investment Workbench: http://172.20.10.2:[PORT]/workbench")
        logger.info("🔗 Alternative IP: http://10.14.0.2:[PORT]")
        logger.info("")
        logger.info("⚠️  [PORT] will be displayed when server starts (usually 8005-8007)")
        logger.info("📱 Share these URLs with others to give them access!")
        logger.info("=" * 80)
        logger.info("")
        
        # Launch the professional streaming server with sophisticated engine
        subprocess.run([
            sys.executable, 
            str(server_path)
        ], env=env, check=True)
        
        # Post-startup message (this won't execute until server stops)
        logger.info("")
        logger.info("🌍 SERVER READY FOR PUBLIC ACCESS!")
        logger.info("📍 Final accessible URLs:")
        logger.info("🔗 http://172.20.10.2:8006 (or current port shown above)")
        logger.info("🔗 http://10.14.0.2:8006 (alternative)")
        logger.info("📱 Share these URLs for network access!")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to start professional streaming server: {e}")
        logger.error("❌ Please check the server configuration and try again")
            
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()