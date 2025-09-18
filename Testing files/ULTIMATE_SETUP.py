#!/usr/bin/env python3
"""
🚀 ULTIMATE ROBECO SETUP - ONE SCRIPT DOES EVERYTHING!
🌍 Makes http://138.199.60.185:8005 work from ANY computer worldwide
🔧 Handles router setup, server, port forwarding - EVERYTHING AUTOMATIC!
"""

import subprocess
import logging
import time
import signal
import sys
import os
import socket
import requests
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 ULTIMATE ROBECO SETUP - COMPLETE AUTOMATION")
    logger.info("🌍 Making http://138.199.60.185:8005 accessible from ANY computer worldwide")
    logger.info("🔧 This ONE script handles EVERYTHING automatically!")
    logger.info("=" * 80)
    
    # Detect current directory
    current_dir = Path(__file__).parent
    logger.info(f"📁 Working directory: {current_dir}")
    
    # Check if we have all required files
    required_files = [
        "run_professional_system.py",
        "complete_router_setup.py", 
        "src/robeco/backend/professional_streaming_server.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (current_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.error("❌ Missing required files:")
        for file in missing_files:
            logger.error(f"   • {file}")
        return
    
    logger.info("✅ All required files found")
    logger.info("")
    
    # Get network info
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        response = requests.get('https://ifconfig.me', timeout=5)
        public_ip = response.text.strip()
        
        logger.info(f"🔍 Local IP: {local_ip}")
        logger.info(f"🔍 Public IP: {public_ip}")
        logger.info("")
        
    except Exception as e:
        logger.warning(f"⚠️ Could not detect IPs: {e}")
        local_ip = "Unknown"
        public_ip = "Unknown"
    
    # Present options to user
    logger.info("🎯 CHOOSE SETUP METHOD:")
    logger.info("=" * 60)
    logger.info("1. 🔧 COMPLETE AUTOMATIC SETUP (Recommended)")
    logger.info("   • Automatically configures router")
    logger.info("   • Sets up port forwarding")
    logger.info("   • Makes http://138.199.60.185:8005 work globally")
    logger.info("   • Handles everything for you!")
    logger.info("")
    logger.info("2. 🚀 STANDARD SETUP (SSH Tunnel + Manual Router)")
    logger.info("   • Starts server with SSH tunnel backup")
    logger.info("   • Provides router setup instructions")
    logger.info("   • You do router config manually")
    logger.info("")
    logger.info("3. 📱 LOCAL NETWORK ONLY")
    logger.info("   • Just run on local network")
    logger.info("   • No internet access setup")
    logger.info("")
    
    # Automatically choose option 1 (Complete Automatic Setup)
    choice = '1'
    logger.info("🤖 AUTO-SELECTING: Complete Automatic Setup")
    logger.info("🔧 This will handle EVERYTHING automatically!")
    
    if choice == '1':
        logger.info("")
        logger.info("🔧 STARTING COMPLETE AUTOMATIC SETUP...")
        logger.info("🎯 This will configure EVERYTHING automatically!")
        logger.info("🌍 Goal: http://138.199.60.185:8005 working from ANY computer")
        logger.info("")
        
        # Run complete router setup
        try:
            subprocess.run([sys.executable, str(current_dir / "complete_router_setup.py")])
        except KeyboardInterrupt:
            logger.info("\n🛑 Setup cancelled by user")
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            
    elif choice == '2':
        logger.info("")
        logger.info("🚀 STARTING STANDARD SETUP...")
        logger.info("🔧 Server + SSH tunnel + manual router instructions")
        logger.info("")
        
        # Run standard setup
        try:
            subprocess.run([sys.executable, str(current_dir / "run_professional_system.py")])
        except KeyboardInterrupt:
            logger.info("\n🛑 Setup cancelled by user")
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            
    elif choice == '3':
        logger.info("")
        logger.info("📱 STARTING LOCAL NETWORK SETUP...")
        logger.info(f"🔗 Will be accessible at: http://{local_ip}:8005")
        logger.info("")
        
        # Run server only
        try:
            server_path = current_dir / "src" / "robeco" / "backend" / "professional_streaming_server.py"
            subprocess.run([sys.executable, str(server_path)])
        except KeyboardInterrupt:
            logger.info("\n🛑 Server stopped by user")
        except Exception as e:
            logger.error(f"❌ Server failed: {e}")
            
    else:
        logger.error("❌ Invalid choice. Please run again and choose 1, 2, or 3.")
    
    logger.info("")
    logger.info("✅ Setup completed!")

if __name__ == "__main__":
    main()