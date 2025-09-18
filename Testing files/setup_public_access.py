#!/usr/bin/env python3
"""
Setup Public Internet Access for Robeco Reporting System
Creates a secure tunnel to make your app accessible from anywhere
"""

import subprocess
import sys
import os
import logging
import time
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ ngrok is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    return False

def install_ngrok():
    """Install ngrok via homebrew on macOS"""
    logger.info("📦 Installing ngrok...")
    try:
        # Install via homebrew
        subprocess.run(['brew', 'install', 'ngrok/ngrok/ngrok'], check=True)
        logger.info("✅ ngrok installed successfully")
        return True
    except subprocess.CalledProcessError:
        logger.error("❌ Failed to install ngrok via homebrew")
        logger.info("📋 Please install manually:")
        logger.info("   1. Visit: https://ngrok.com/download")
        logger.info("   2. Download and install ngrok")
        logger.info("   3. Run: ngrok authtoken YOUR_TOKEN")
        return False
    except FileNotFoundError:
        logger.error("❌ Homebrew not found. Please install ngrok manually:")
        logger.info("   1. Visit: https://ngrok.com/download")
        logger.info("   2. Download and install ngrok")
        return False

def setup_ngrok_auth():
    """Setup ngrok authentication"""
    logger.info("🔐 Setting up ngrok authentication...")
    logger.info("📋 Steps to get your auth token:")
    logger.info("   1. Go to: https://dashboard.ngrok.com/get-started/your-authtoken")
    logger.info("   2. Sign up/login to ngrok (free account)")
    logger.info("   3. Copy your authtoken")
    
    token = input("\n🔑 Paste your ngrok authtoken here (or press Enter to skip): ").strip()
    
    if token:
        try:
            subprocess.run(['ngrok', 'authtoken', token], check=True)
            logger.info("✅ ngrok authenticated successfully")
            return True
        except subprocess.CalledProcessError:
            logger.error("❌ Failed to authenticate ngrok")
            return False
    else:
        logger.warning("⚠️  Skipping authentication - limited to 2 hour sessions")
        return True

def start_tunnel(port=8005):
    """Start ngrok tunnel for the specified port"""
    logger.info(f"🌐 Starting ngrok tunnel for port {port}...")
    
    try:
        # Start ngrok tunnel in background
        process = subprocess.Popen(
            ['ngrok', 'http', str(port), '--log=stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for ngrok to start
        time.sleep(3)
        
        # Get tunnel info
        try:
            result = subprocess.run(['curl', '-s', 'localhost:4040/api/tunnels'], 
                                   capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                tunnels = data.get('tunnels', [])
                if tunnels:
                    public_url = tunnels[0]['public_url']
                    logger.info("🎉 Tunnel created successfully!")
                    logger.info("=" * 60)
                    logger.info("🌍 PUBLIC ACCESS URL:")
                    logger.info(f"🔗 {public_url}")
                    logger.info(f"🔗 {public_url}/workbench")
                    logger.info("=" * 60)
                    logger.info("📱 Share this URL with anyone worldwide!")
                    logger.info("⏰ Tunnel will stay active while this runs")
                    return process, public_url
        except:
            pass
            
        logger.info("🔄 Tunnel started, but couldn't fetch URL automatically")
        logger.info("📋 Check ngrok dashboard at: http://localhost:4040")
        return process, None
        
    except Exception as e:
        logger.error(f"❌ Failed to start tunnel: {e}")
        return None, None

def main():
    """Main setup function"""
    logger.info("🚀 Setting up Public Internet Access for Robeco Reporting")
    logger.info("=" * 60)
    
    # Check if ngrok is installed
    if not check_ngrok_installed():
        logger.info("📦 ngrok not found. Installing...")
        if not install_ngrok():
            return
    
    # Setup authentication
    if not setup_ngrok_auth():
        logger.error("❌ Authentication failed")
        return
    
    # Start tunnel
    logger.info("\n🌐 Creating secure tunnel...")
    process, public_url = start_tunnel()
    
    if process:
        logger.info("\n📋 INSTRUCTIONS:")
        logger.info("1. Keep this window open to maintain the tunnel")
        logger.info("2. In another terminal, run your app:")
        logger.info("   python run_professional_system.py")
        logger.info("3. Your app will be accessible worldwide via the URL above")
        logger.info("\n⌨️  Press Ctrl+C to stop the tunnel")
        
        try:
            # Keep running until interrupted
            process.wait()
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping tunnel...")
            process.terminate()
            logger.info("✅ Tunnel stopped")
    else:
        logger.error("❌ Failed to create tunnel")

if __name__ == "__main__":
    main()