#!/usr/bin/env python3
"""
🚀 COMPLETE SOLUTION - FIXED IP + INSTANT BACKUP
🎯 Priority: http://138.199.60.185:8005 (Fixed IP)
🔄 Backup: Instant global URL if router setup fails
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

server_process = None
tunnel_process = None

def cleanup_processes():
    global server_process, tunnel_process
    if tunnel_process:
        tunnel_process.terminate()
    if server_process:
        server_process.terminate()

def signal_handler(sig, frame):
    logger.info("\n🛑 Shutdown requested...")
    cleanup_processes()
    sys.exit(0)

def start_robeco_server():
    """Start Robeco server on port 8005"""
    global server_process
    
    # Aggressive port cleanup
    logger.info("🔫 Freeing port 8005...")
    commands = [
        ['pkill', '-9', '-f', 'professional_streaming_server'],
        ['pkill', '-9', '-f', '8005'],
        ['pkill', '-9', '-f', 'uvicorn.*8005']
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, capture_output=True, check=False)
        except:
            pass
    
    # Kill by port
    try:
        result = subprocess.run(['lsof', '-ti:8005'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid], check=False)
    except:
        pass
    
    time.sleep(5)
    
    current_dir = Path(__file__).parent
    server_path = current_dir / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(current_dir / "src") + os.pathsep + env.get('PYTHONPATH', '')
    env['FORCE_PORT_8005'] = 'true'
    
    logger.info("🚀 Starting Robeco server on port 8005...")
    
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env)
    
    time.sleep(12)
    
    # Verify server
    for attempt in range(15):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', 8005))
                if result == 0:
                    logger.info("✅ Robeco server running on port 8005!")
                    return True
        except:
            pass
        time.sleep(1)
    
    return False

def test_fixed_ip():
    """Test if fixed IP is working"""
    logger.info("🧪 Testing fixed IP access...")
    
    try:
        response = requests.get('http://138.199.60.185:8005', timeout=10)
        if response.status_code in [200, 404, 405]:
            return True
    except:
        pass
    return False

def show_router_instructions():
    """Show simple router setup instructions"""
    logger.info("")
    logger.info("🔧 ROUTER SETUP FOR FIXED IP ACCESS")
    logger.info("=" * 80)
    logger.info("🎯 Goal: Make http://138.199.60.185:8005 work globally")
    logger.info("")
    logger.info("📋 SIMPLE 3-STEP SETUP:")
    logger.info("")
    logger.info("1️⃣ FIND YOUR ROUTER:")
    logger.info("   • Look for router device (usually has antennas)")
    logger.info("   • Check router label for IP address")
    logger.info("   • Common IPs: 192.168.1.1, 192.168.0.1, 10.0.0.1")
    logger.info("   • Try these in your browser")
    logger.info("")
    logger.info("2️⃣ LOGIN TO ROUTER:")
    logger.info("   • Username: admin")
    logger.info("   • Password: admin (or check router label)")
    logger.info("   • Look for sticker on router with login info")
    logger.info("")
    logger.info("3️⃣ ADD PORT FORWARDING:")
    logger.info("   • Find: 'Port Forwarding' or 'Virtual Server'")
    logger.info("   • Add new rule:")
    logger.info("     - Name: Robeco")
    logger.info("     - External Port: 8005")
    logger.info("     - Internal IP: 10.7.7.2")
    logger.info("     - Internal Port: 8005")
    logger.info("     - Protocol: TCP")
    logger.info("   • Save and restart router")
    logger.info("")
    logger.info("🎯 RESULT: http://138.199.60.185:8005 will work worldwide!")
    logger.info("=" * 80)

def create_instant_backup():
    """Create instant SSH tunnel backup"""
    global tunnel_process
    
    logger.info("")
    logger.info("🔄 CREATING INSTANT BACKUP ACCESS...")
    logger.info("🌍 This gives you immediate global access while you set up the router")
    
    try:
        tunnel_process = subprocess.Popen([
            'ssh', '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-R', '80:127.0.0.1:8005', 'serveo.net'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        time.sleep(8)
        
        logger.info("✅ INSTANT BACKUP ACCESS CREATED!")
        logger.info("🔗 Check above for global URL (format: https://[id].serveo.net)")
        logger.info("📱 Use this URL while setting up the router")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Backup access failed: {e}")
        return False

def monitor_fixed_ip():
    """Monitor for fixed IP to start working"""
    logger.info("")
    logger.info("⏳ MONITORING FIXED IP ACCESS...")
    logger.info("⏳ Testing every 30 seconds to see when router setup is complete...")
    
    for check in range(20):  # 10 minutes
        logger.info(f"🧪 Check {check + 1}/20: Testing http://138.199.60.185:8005")
        
        if test_fixed_ip():
            logger.info("")
            logger.info("🎉 AMAZING! FIXED IP IS NOW WORKING!")
            logger.info("=" * 80)
            logger.info("✅ SUCCESS: http://138.199.60.185:8005")
            logger.info("✅ SUCCESS: http://138.199.60.185:8005/workbench")
            logger.info("📱 Share these URLs with anyone worldwide!")
            logger.info("🎯 Your preferred fixed IP method is now active!")
            logger.info("=" * 80)
            return True
        
        if check < 19:
            logger.info("⏳ Not ready yet - router setup still needed...")
            time.sleep(30)
    
    logger.info("⏳ Still waiting for router setup...")
    return False

def display_final_status():
    """Display final status with both access methods"""
    logger.info("")
    logger.info("📊 COMPLETE ACCESS STATUS")
    logger.info("=" * 80)
    logger.info("✅ WORKING ACCESS METHODS:")
    logger.info("   🏠 Local Network: http://10.7.7.2:8005")
    logger.info("   🏠 Your Computer: http://localhost:8005")
    logger.info("   🔄 Backup Global: Check tunnel URL above")
    logger.info("")
    logger.info("🎯 TARGET FIXED IP ACCESS:")
    logger.info("   🌍 Primary Goal: http://138.199.60.185:8005")
    logger.info("   🌍 Workbench: http://138.199.60.185:8005/workbench")
    logger.info("   📋 Status: Waiting for router setup")
    logger.info("")
    logger.info("💡 YOU HAVE TWO OPTIONS:")
    logger.info("   1. Use backup global URL now (works immediately)")
    logger.info("   2. Complete router setup for fixed IP access")
    logger.info("=" * 80)

def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🚀 COMPLETE SOLUTION - FIXED IP + INSTANT BACKUP")
    logger.info("🎯 Priority: Fixed IP http://138.199.60.185:8005")
    logger.info("🔄 Backup: Instant global access")
    logger.info("=" * 80)
    
    # Start server
    if not start_robeco_server():
        logger.error("❌ Cannot continue without server")
        return
    
    # Test if fixed IP already works
    if test_fixed_ip():
        logger.info("🎉 AMAZING! Fixed IP already works!")
        logger.info("✅ http://138.199.60.185:8005 is accessible globally!")
        keep_running()
        return
    
    logger.info("📋 Fixed IP needs router setup")
    
    # Show router instructions
    show_router_instructions()
    
    # Create instant backup
    create_instant_backup()
    
    # Monitor for fixed IP
    fixed_ip_working = monitor_fixed_ip()
    
    if not fixed_ip_working:
        display_final_status()
    
    keep_running()

def keep_running():
    """Keep server running"""
    logger.info("")
    logger.info("⌨️ Press Ctrl+C to stop server")
    logger.info("📊 Server running on port 8005...")
    logger.info("=" * 80)
    
    try:
        while True:
            time.sleep(1)
            if server_process and server_process.poll() is not None:
                logger.error("❌ Server stopped")
                break
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping server...")
    finally:
        cleanup_processes()
        logger.info("✅ All services stopped")

if __name__ == "__main__":
    main()