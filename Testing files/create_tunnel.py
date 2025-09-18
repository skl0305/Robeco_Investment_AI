#!/usr/bin/env python3
"""
Simple tunnel creator for Robeco server
Run this AFTER the server is running
"""

import time
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def check_server_running():
    """Check if server is running on port 8005"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', 8005))
            return result == 0
    except:
        return False

def create_ssh_tunnel():
    """Create SSH tunnel using serveo.net"""
    logger.info("🚀 Creating SSH tunnel...")
    
    tunnel_cmd = [
        'ssh', '-o', 'StrictHostKeyChecking=no', 
        '-o', 'UserKnownHostsFile=/dev/null',
        '-R', '80:127.0.0.1:8005', 'serveo.net'
    ]
    
    try:
        tunnel_process = subprocess.Popen(
            tunnel_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True
        )
        
        logger.info("⏳ Establishing tunnel...")
        
        # Read output to find the URL
        tunnel_url = None
        for i in range(20):  # Wait up to 20 seconds
            time.sleep(1)
            
            if tunnel_process.poll() is not None:
                logger.error("❌ Tunnel process stopped")
                break
            
            # Try to read line by line
            try:
                line = tunnel_process.stdout.readline()
                if line:
                    print(f"Tunnel output: {line.strip()}")
                    
                    # Look for serveo.net URL
                    if 'serveo.net' in line and 'https://' in line:
                        import re
                        url_match = re.search(r'https://[a-zA-Z0-9-]+\.serveo\.net', line)
                        if url_match:
                            tunnel_url = url_match.group(0)
                            break
            except:
                continue
        
        if tunnel_url:
            logger.info("🎉 SUCCESS! Tunnel created!")
            logger.info("=" * 80)
            logger.info(f"🌍 YOUR GLOBAL URL: {tunnel_url}")
            logger.info(f"🔧 WORKBENCH: {tunnel_url}/workbench")
            logger.info("=" * 80)
            logger.info("🌐 Share these URLs with ANYONE worldwide!")
            logger.info("✅ No HTTP 502 errors!")
            logger.info("⌨️  Press Ctrl+C to stop tunnel")
            logger.info("=" * 80)
            
            # Keep tunnel alive
            try:
                tunnel_process.wait()
            except KeyboardInterrupt:
                logger.info("\n🛑 Stopping tunnel...")
                tunnel_process.terminate()
        else:
            logger.error("❌ Could not extract tunnel URL")
            tunnel_process.terminate()
            
    except Exception as e:
        logger.error(f"❌ Tunnel failed: {e}")

def create_ngrok_tunnel():
    """Create ngrok tunnel"""
    try:
        import ngrok
        
        logger.info("🚀 Creating ngrok tunnel...")
        
        # Set authtoken
        authtoken = "32icGzoNAvSORFv3anOyE7Qeon6_6qzfyfbDaCh4AekUVWiZi"
        
        # Try different ngrok methods
        try:
            # Method 1: Use forward
            tunnel = ngrok.forward(8005, authtoken=authtoken)
            url = tunnel.url()
        except:
            try:
                # Method 2: Use connect
                tunnel = ngrok.connect(8005, auth_token=authtoken)
                url = tunnel.public_url
            except:
                # Method 3: Use environment variable approach
                import os
                os.environ['NGROK_AUTHTOKEN'] = authtoken
                tunnel = ngrok.connect(8005)
                url = tunnel.public_url
        
        logger.info("🎉 NGROK TUNNEL CREATED!")
        logger.info("=" * 80)
        logger.info(f"🌍 YOUR GLOBAL URL: {url}")
        logger.info(f"🔧 WORKBENCH: {url}/workbench")
        logger.info("=" * 80)
        logger.info("🌐 Share these URLs with ANYONE worldwide!")
        logger.info("✅ Professional ngrok reliability!")
        logger.info("⌨️  Press Ctrl+C to stop tunnel")
        logger.info("=" * 80)
        
        # Keep tunnel alive
        try:
            input("Press Enter to stop tunnel...")
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping ngrok tunnel...")
        
        ngrok.kill()
        return True
        
    except ImportError:
        logger.error("❌ ngrok not installed. Run: pip install ngrok")
        return False
    except Exception as e:
        logger.error(f"❌ ngrok failed: {e}")
        return False

def main():
    logger.info("🌍 Robeco Global Tunnel Creator")
    logger.info("=" * 50)
    
    # Check if server is running
    if not check_server_running():
        logger.error("❌ Server not running on port 8005")
        logger.info("💡 Please start the server first:")
        logger.info("   python start_with_tunnel.py")
        return
    
    logger.info("✅ Server detected on port 8005")
    logger.info("")
    logger.info("Choose tunnel method:")
    logger.info("1. 🔗 SSH Tunnel (serveo.net) - Free")
    logger.info("2. 🚀 ngrok Tunnel - Professional")
    logger.info("3. 🔧 Manual Instructions")
    
    choice = input("Choose (1/2/3): ").strip()
    
    if choice == '1':
        create_ssh_tunnel()
    elif choice == '2':
        if not create_ngrok_tunnel():
            logger.info("💡 Falling back to SSH tunnel...")
            create_ssh_tunnel()
    elif choice == '3':
        logger.info("")
        logger.info("🔧 MANUAL TUNNEL SETUP:")
        logger.info("📋 Open NEW terminal and run:")
        logger.info("")
        logger.info("   ssh -R 80:127.0.0.1:8005 serveo.net")
        logger.info("")
        logger.info("🎯 You'll get a URL like: https://abc123.serveo.net")
        logger.info("🌐 Share that URL worldwide!")
    else:
        logger.error("❌ Invalid choice")

if __name__ == "__main__":
    main()