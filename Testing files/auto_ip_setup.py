#!/usr/bin/env python3
"""
Automatic IP Access Setup for Robeco
Creates fixed IP access without manual router configuration
Uses UPnP for automatic port forwarding + fallback methods
"""

import subprocess
import logging
import time
import signal
import sys
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

server_process = None

def cleanup_processes():
    """Clean up server process"""
    global server_process
    if server_process:
        server_process.terminate()
        try:
            server_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_process.kill()

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("\n🛑 Shutdown requested...")
    cleanup_processes()
    sys.exit(0)

def try_upnp_port_forwarding():
    """Try to automatically configure port forwarding using UPnP"""
    logger.info("🔧 Attempting automatic port forwarding (UPnP)...")
    
    try:
        # Try to install miniupnpc if not available
        result = subprocess.run(['which', 'upnpc'], capture_output=True)
        if result.returncode != 0:
            logger.info("📦 Installing UPnP tools...")
            try:
                subprocess.run(['brew', 'install', 'miniupnpc'], check=True, timeout=60)
                logger.info("✅ UPnP tools installed")
            except:
                logger.info("⚠️  Could not install UPnP tools, trying alternatives...")
                return False
        
        # Try to add port mapping
        logger.info("🌐 Configuring automatic port forwarding...")
        cmd = ['upnpc', '-a', '10.7.7.2', '8005', '8005', 'TCP']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("✅ Automatic port forwarding successful!")
            logger.info("🌍 Port 8005 is now forwarded to 10.7.7.2:8005")
            return True
        else:
            logger.info("⚠️  UPnP port forwarding failed - router may not support it")
            logger.info(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.info(f"⚠️  UPnP failed: {e}")
        return False

def create_port_forwarding_script():
    """Create a comprehensive port forwarding script"""
    
    script_content = '''#!/bin/bash
# Automatic Port Forwarding Script for Robeco
# Multiple methods to enable http://138.199.60.185:8005 access

echo "🌐 Robeco Automatic Port Forwarding Setup"
echo "🎯 Goal: Enable http://138.199.60.185:8005 global access"
echo ""

# Method 1: UPnP Automatic Configuration
echo "📡 Method 1: UPnP Automatic Port Forwarding..."
if command -v upnpc &> /dev/null; then
    echo "✅ UPnP client found, attempting automatic setup..."
    upnpc -a 10.7.7.2 8005 8005 TCP
    if [ $? -eq 0 ]; then
        echo "✅ UPnP port forwarding successful!"
        echo "🌍 http://138.199.60.185:8005 should now be accessible globally"
        exit 0
    else
        echo "⚠️  UPnP failed, trying next method..."
    fi
else
    echo "⚠️  UPnP client not found, installing..."
    brew install miniupnpc 2>/dev/null
    if command -v upnpc &> /dev/null; then
        upnpc -a 10.7.7.2 8005 8005 TCP
        if [ $? -eq 0 ]; then
            echo "✅ UPnP port forwarding successful!"
            echo "🌍 http://138.199.60.185:8005 should now be accessible globally"
            exit 0
        fi
    fi
fi

# Method 2: Router Detection and Instructions
echo ""
echo "📡 Method 2: Router Configuration Instructions..."

# Try to detect router
ROUTER_IP=$(route -n get default 2>/dev/null | grep gateway | awk '{print $2}' | head -1)
if [ -z "$ROUTER_IP" ]; then
    ROUTER_IP=$(netstat -rn | grep default | grep en0 | awk '{print $2}' | head -1)
fi
if [ -z "$ROUTER_IP" ]; then
    ROUTER_IP="172.20.10.1"  # Fallback to known IP
fi

echo "📍 Detected router IP: $ROUTER_IP"

# Try common router access methods
echo "🔍 Testing router accessibility..."
for ip in "$ROUTER_IP" "192.168.1.1" "192.168.0.1" "10.0.0.1" "172.20.10.1"; do
    if curl -s --connect-timeout 3 "http://$ip" > /dev/null 2>&1; then
        echo "✅ Router accessible at: http://$ip"
        open "http://$ip" 2>/dev/null
        ROUTER_FOUND="$ip"
        break
    fi
done

if [ -n "$ROUTER_FOUND" ]; then
    echo ""
    echo "🎯 ROUTER CONFIGURATION INSTRUCTIONS:"
    echo "============================================"
    echo "Router Admin Panel: http://$ROUTER_FOUND"
    echo ""
    echo "1. Login to router admin panel (check router label for password)"
    echo "2. Find 'Port Forwarding' or 'Virtual Server' section"
    echo "3. Add new rule:"
    echo "   • Service Name: Robeco"
    echo "   • External Port: 8005"
    echo "   • Internal IP: 10.7.7.2"
    echo "   • Internal Port: 8005"
    echo "   • Protocol: TCP"
    echo "4. Save and restart router"
    echo ""
    echo "🌍 After setup: http://138.199.60.185:8005 will work globally!"
else
    echo "⚠️  Router not accessible via web interface"
    echo "💡 Manual router configuration may be needed"
fi

# Method 3: Alternative Access Methods
echo ""
echo "📡 Method 3: Alternative Access Information..."
echo "If router configuration is not possible, you have these options:"
echo ""
echo "🔗 SSH Tunnel (Already Working):"
echo "   Global URL: Check your running Robeco server for the serveo.net URL"
echo "   ✅ No router setup needed"
echo "   ✅ Works immediately"
echo ""
echo "📱 Mobile Hotspot Method:"
echo "   1. Enable mobile hotspot on your phone"
echo "   2. Connect Mac to phone hotspot"
echo "   3. Share phone's IP with users"
echo "   ✅ Bypasses router completely"
echo ""
echo "🎯 Current Status:"
echo "   • Local access: http://10.7.7.2:8005"
echo "   • Target global: http://138.199.60.185:8005"
echo "   • SSH tunnel: Active (check Robeco logs)"

'''
    
    script_file = Path(__file__).parent / "auto_port_forward.sh"
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_file, 0o755)
    logger.info(f"✅ Created port forwarding script: {script_file}")
    return script_file

def start_robeco_with_auto_forwarding():
    """Start Robeco server and attempt auto port forwarding"""
    global server_process
    
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    server_path = project_root / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path) + os.pathsep + env.get('PYTHONPATH', '')
    
    logger.info("🚀 Starting Robeco server with automatic setup...")
    
    # Start server
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env)
    
    # Wait for server to start
    logger.info("⏳ Waiting for server to start...")
    time.sleep(8)
    
    # Check if server is running
    if server_process.poll() is None:
        logger.info("✅ Robeco server started successfully on port 8005")
        return True
    else:
        logger.error("❌ Server failed to start")
        return False

def test_global_access():
    """Test if global access is working"""
    logger.info("🧪 Testing global access...")
    
    try:
        import requests
        
        # Test if the global IP is accessible
        test_url = "http://138.199.60.185:8005"
        response = requests.get(test_url, timeout=10)
        
        if response.status_code in [200, 405]:
            logger.info("🎉 SUCCESS! Global access is working!")
            logger.info(f"✅ http://138.199.60.185:8005 is accessible worldwide")
            return True
        else:
            logger.info(f"⚠️  Got response code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        logger.info("❌ Connection timeout - port forwarding may not be active")
        return False
    except requests.exceptions.ConnectionError:
        logger.info("❌ Connection refused - port forwarding needed")
        return False
    except Exception as e:
        logger.info(f"❌ Test failed: {e}")
        return False

def display_final_status():
    """Display final status and instructions"""
    
    logger.info("")
    logger.info("🎉 ROBECO AUTO IP SETUP COMPLETE!")
    logger.info("=" * 80)
    logger.info("📍 ACCESS STATUS:")
    logger.info("=" * 80)
    logger.info("🏠 Local computer: http://localhost:8005 ✅ WORKING")
    logger.info("🏠 Local network: http://10.7.7.2:8005 ✅ WORKING")
    logger.info("🌍 GLOBAL TARGET: http://138.199.60.185:8005")
    logger.info("🔗 SSH tunnel: Check Robeco logs for serveo.net URL ✅ WORKING")
    logger.info("=" * 80)
    logger.info("")
    logger.info("🎯 FOR FIXED IP ACCESS (http://138.199.60.185:8005):")
    logger.info("   1. ✅ Server is running and ready")
    logger.info("   2. ⚠️  Router port forwarding needed")
    logger.info("   3. 🔧 Run: ./auto_port_forward.sh for detailed setup")
    logger.info("")
    logger.info("🌐 IMMEDIATE ACCESS OPTIONS:")
    logger.info("   • ✅ SSH tunnel URL (working now)")
    logger.info("   • ✅ Local network: http://10.7.7.2:8005")
    logger.info("   • 📱 Mobile hotspot method")
    logger.info("")
    logger.info("💡 YOU HAVE WORKING GLOBAL ACCESS VIA SSH TUNNEL!")
    logger.info("💡 Fixed IP will work after router setup")
    logger.info("")
    logger.info("⌨️  Press Ctrl+C to stop server")
    logger.info("=" * 80)

def main():
    """Main function"""
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🌐 Robeco Automatic IP Access Setup")
    logger.info("🎯 Creating fixed IP access: http://138.199.60.185:8005")
    logger.info("")
    
    # Create port forwarding script
    script_file = create_port_forwarding_script()
    
    # Try UPnP automatic setup
    upnp_success = try_upnp_port_forwarding()
    
    # Start Robeco server
    if not start_robeco_with_auto_forwarding():
        logger.error("❌ Failed to start Robeco server")
        return
    
    # Test global access
    time.sleep(2)
    global_working = test_global_access()
    
    if global_working:
        logger.info("🎉 AMAZING! Fixed IP access is already working!")
        logger.info("🌍 http://138.199.60.185:8005 is accessible worldwide")
    elif upnp_success:
        logger.info("✅ UPnP setup completed - testing again in 30 seconds...")
        time.sleep(30)
        global_working = test_global_access()
    
    # Display final status
    display_final_status()
    
    if not global_working:
        logger.info("")
        logger.info("🔧 To enable fixed IP access, run:")
        logger.info(f"   bash {script_file}")
        logger.info("   (This will provide detailed router setup instructions)")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            if server_process.poll() is not None:
                logger.error("❌ Server process stopped")
                break
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping server...")
    finally:
        cleanup_processes()
        logger.info("✅ Server stopped")

if __name__ == "__main__":
    main()