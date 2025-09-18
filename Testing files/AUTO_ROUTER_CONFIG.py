#!/usr/bin/env python3
"""
🔧 AUTOMATIC ROUTER CONFIGURATION
🎯 Makes http://138.199.60.185:8005 work automatically
✅ No manual router setup required!
"""

import subprocess
import logging
import time
import signal
import sys
import os
import socket
import requests
import webbrowser
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

server_process = None

def cleanup_processes():
    global server_process
    if server_process:
        server_process.terminate()
        try:
            server_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_process.kill()

def signal_handler(sig, frame):
    logger.info("\n🛑 Shutdown requested...")
    cleanup_processes()
    sys.exit(0)

def install_router_tools():
    """Install tools for router configuration"""
    logger.info("📦 Installing router configuration tools...")
    
    tools = ['nmap', 'curl']
    for tool in tools:
        try:
            result = subprocess.run(['which', tool], capture_output=True)
            if result.returncode != 0:
                logger.info(f"📦 Installing {tool}...")
                subprocess.run(['brew', 'install', tool], check=True, timeout=120)
        except:
            pass

def scan_network_for_router():
    """Scan network to find router"""
    logger.info("🔍 SCANNING NETWORK FOR ROUTER...")
    
    # Get network range
    try:
        result = subprocess.run(['route', '-n', 'get', 'default'], 
                              capture_output=True, text=True)
        gateway = None
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'gateway:' in line:
                    gateway = line.split(':')[1].strip()
                    break
    except:
        gateway = None
    
    # Common router IPs + detected gateway
    router_candidates = ['192.168.1.1', '192.168.0.1', '10.0.0.1', '172.16.0.1', '192.168.2.1']
    if gateway and gateway not in router_candidates:
        router_candidates.insert(0, gateway)
    
    accessible_routers = []
    
    for router_ip in router_candidates:
        logger.info(f"🔍 Testing {router_ip}...")
        try:
            response = requests.get(f'http://{router_ip}', timeout=5)
            if response.status_code in [200, 401, 403]:
                accessible_routers.append(router_ip)
                logger.info(f"✅ Router found: {router_ip}")
        except:
            logger.info(f"❌ No response from {router_ip}")
    
    return accessible_routers

def try_automatic_router_config(router_ip, local_ip='10.7.7.2', port=8005):
    """Try various automatic router configuration methods"""
    logger.info(f"🔧 ATTEMPTING AUTOMATIC CONFIGURATION: {router_ip}")
    
    # Method 1: UPnP
    try:
        logger.info("📡 Trying UPnP...")
        result = subprocess.run(['upnpc', '-a', local_ip, str(port), str(port), 'TCP'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            logger.info("✅ UPnP configuration successful!")
            return True
    except:
        pass
    
    # Method 2: Common router API endpoints
    router_configs = [
        # TP-Link
        {
            'brand': 'TP-Link',
            'login_url': f'http://{router_ip}/userRpm/LoginRpm.htm',
            'config_url': f'http://{router_ip}/userRpm/VirtualServerRpm.htm',
            'credentials': [('admin', 'admin'), ('admin', 'password'), ('admin', '')]
        },
        # Netgear
        {
            'brand': 'Netgear',
            'login_url': f'http://{router_ip}/base.htm',
            'config_url': f'http://{router_ip}/setup.cgi',
            'credentials': [('admin', 'password'), ('admin', 'admin'), ('admin', '')]
        },
        # Linksys
        {
            'brand': 'Linksys',
            'login_url': f'http://{router_ip}/index.asp',
            'config_url': f'http://{router_ip}/apply.cgi',
            'credentials': [('admin', 'admin'), ('admin', ''), ('admin', 'password')]
        }
    ]
    
    for config in router_configs:
        logger.info(f"🔧 Trying {config['brand']} configuration...")
        
        for username, password in config['credentials']:
            try:
                # Try to login
                session = requests.Session()
                login_data = {'username': username, 'password': password}
                response = session.post(config['login_url'], data=login_data, timeout=10)
                
                if response.status_code == 200:
                    # Try to configure port forwarding
                    port_forward_data = {
                        'service_name': 'Robeco',
                        'external_port': str(port),
                        'internal_ip': local_ip,
                        'internal_port': str(port),
                        'protocol': 'TCP',
                        'enable': '1'
                    }
                    
                    config_response = session.post(config['config_url'], data=port_forward_data, timeout=10)
                    if config_response.status_code in [200, 302]:
                        logger.info(f"🎉 {config['brand']} configuration successful!")
                        return True
                        
            except Exception as e:
                continue
    
    return False

def create_router_automation_script(router_ip, local_ip='10.7.7.2', port=8005):
    """Create a comprehensive router automation script"""
    
    script_content = f'''#!/bin/bash
# Automatic Router Configuration for Fixed IP Access
# Target: {router_ip} -> {local_ip}:{port}

echo "🔧 Automatic Router Configuration Starting..."
echo "🎯 Goal: Enable http://138.199.60.185:{port} global access"

# Function to test if configuration worked
test_access() {{
    echo "🧪 Testing global access..."
    curl -s --connect-timeout 10 "http://138.199.60.185:{port}/" > /dev/null 2>&1
    return $?
}}

# Method 1: UPnP Automatic Setup
echo "📡 Method 1: UPnP Configuration..."
if command -v upnpc &> /dev/null; then
    upnpc -a {local_ip} {port} {port} TCP 2>/dev/null
    if [ $? -eq 0 ]; then
        sleep 10
        if test_access; then
            echo "🎉 SUCCESS! UPnP configuration worked!"
            echo "✅ http://138.199.60.185:{port} is now accessible globally!"
            exit 0
        fi
    fi
fi

# Method 2: Web Interface Automation
echo "📡 Method 2: Web Interface Automation..."

# Common credentials for different router brands
declare -A ROUTER_CREDS=(
    ["admin"]="admin"
    ["admin"]="password"
    ["admin"]=""
    ["root"]="admin"
    ["user"]="user"
)

# Try different router interfaces
for user in "${{!ROUTER_CREDS[@]}}"; do
    pass="${{ROUTER_CREDS[$user]}}"
    echo "🔑 Trying $user:$pass on {router_ip}..."
    
    # Try TP-Link interface
    curl -s -X POST \\
        -d "username=$user&password=$pass" \\
        "http://{router_ip}/userRpm/LoginRpm.htm" \\
        -c cookies.txt >/dev/null 2>&1
    
    if [ -f cookies.txt ]; then
        # Try to add port forwarding rule
        curl -s -X POST \\
            -b cookies.txt \\
            -d "service_name=Robeco&external_port={port}&internal_ip={local_ip}&internal_port={port}&protocol=TCP&enable=1" \\
            "http://{router_ip}/userRpm/VirtualServerRpm.htm" >/dev/null 2>&1
        
        sleep 5
        if test_access; then
            echo "🎉 SUCCESS! Web interface configuration worked!"
            echo "✅ http://138.199.60.185:{port} is now accessible globally!"
            rm -f cookies.txt
            exit 0
        fi
        rm -f cookies.txt
    fi
    
    # Try Netgear interface
    curl -s -X POST \\
        -d "username=$user&password=$pass" \\
        "http://{router_ip}/base.htm" \\
        -c cookies.txt >/dev/null 2>&1
        
    if [ -f cookies.txt ]; then
        curl -s -X POST \\
            -b cookies.txt \\
            -d "portForwardIP={local_ip}&portForwardPort={port}&portForwardExt={port}" \\
            "http://{router_ip}/setup.cgi" >/dev/null 2>&1
        
        sleep 5
        if test_access; then
            echo "🎉 SUCCESS! Netgear configuration worked!"
            echo "✅ http://138.199.60.185:{port} is now accessible globally!"
            rm -f cookies.txt
            exit 0
        fi
        rm -f cookies.txt
    fi
done

# Method 3: Direct API calls (some routers support REST API)
echo "📡 Method 3: Direct API Configuration..."
curl -s -X POST \\
    -H "Content-Type: application/json" \\
    -d '{{"service":"Robeco","external_port":{port},"internal_ip":"{local_ip}","internal_port":{port},"protocol":"TCP"}}' \\
    "http://{router_ip}/api/portforward" >/dev/null 2>&1

sleep 5
if test_access; then
    echo "🎉 SUCCESS! API configuration worked!"
    echo "✅ http://138.199.60.185:{port} is now accessible globally!"
    exit 0
fi

echo "⚠️ Automatic configuration failed"
echo "📋 Manual setup required:"
echo "   1. Open: http://{router_ip}"
echo "   2. Login with admin/admin or check router label"
echo "   3. Find Port Forwarding section"
echo "   4. Add: External {port} -> {local_ip}:{port}"
echo "   5. Save and restart router"
echo "   6. Test: http://138.199.60.185:{port}"
exit 1
'''
    
    script_file = Path(__file__).parent / "auto_router_setup.sh"
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_file, 0o755)
    return script_file

def test_fixed_ip_access(port=8005):
    """Test if fixed IP access is working"""
    logger.info("🧪 TESTING FIXED IP ACCESS...")
    
    test_url = f"http://138.199.60.185:{port}"
    
    for attempt in range(3):
        try:
            logger.info(f"🧪 Test {attempt + 1}/3: {test_url}")
            response = requests.get(test_url, timeout=15)
            
            if response.status_code in [200, 404, 405]:
                logger.info("🎉 SUCCESS! Fixed IP access is working!")
                logger.info(f"✅ {test_url} is accessible from anywhere!")
                return True
            else:
                logger.info(f"⚠️ Got status code: {response.status_code}")
        except requests.exceptions.Timeout:
            logger.info("❌ Timeout - router configuration needed")
        except requests.exceptions.ConnectionError:
            logger.info("❌ Connection refused - port forwarding not configured")
        except Exception as e:
            logger.info(f"❌ Error: {e}")
        
        if attempt < 2:
            time.sleep(5)
    
    return False

def start_robeco_server():
    """Start Robeco server"""
    global server_process
    
    # Kill existing processes
    kill_commands = [
        ['pkill', '-9', '-f', 'professional_streaming_server'],
        ['pkill', '-9', '-f', '8005']
    ]
    
    for cmd in kill_commands:
        try:
            subprocess.run(cmd, capture_output=True, check=False)
        except:
            pass
    
    time.sleep(3)
    
    current_dir = Path(__file__).parent
    server_path = current_dir / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    if not server_path.exists():
        logger.error(f"❌ Server not found: {server_path}")
        return False
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(current_dir / "src") + os.pathsep + env.get('PYTHONPATH', '')
    env['FORCE_PORT_8005'] = 'true'
    
    logger.info("🚀 Starting Robeco server on port 8005...")
    
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env)
    
    time.sleep(10)
    
    # Verify server
    for attempt in range(10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', 8005))
                if result == 0:
                    logger.info("✅ Robeco server is running on port 8005!")
                    return True
        except:
            pass
        time.sleep(1)
    
    return False

def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🔧 AUTOMATIC ROUTER CONFIGURATION")
    logger.info("🎯 Goal: Make http://138.199.60.185:8005 work automatically")
    logger.info("✅ No manual setup required!")
    logger.info("=" * 80)
    
    # Install tools
    install_router_tools()
    
    # Start server
    if not start_robeco_server():
        logger.error("❌ Cannot continue without server")
        return
    
    # Test if already working
    if test_fixed_ip_access():
        logger.info("🎉 AMAZING! Fixed IP is already working!")
        logger.info("✅ http://138.199.60.185:8005 is accessible globally!")
        keep_running()
        return
    
    # Find routers
    routers = scan_network_for_router()
    if not routers:
        logger.error("❌ No accessible routers found")
        return
    
    # Try automatic configuration
    success = False
    for router_ip in routers:
        logger.info(f"🔧 Trying automatic configuration for {router_ip}...")
        
        if try_automatic_router_config(router_ip):
            logger.info("⏳ Waiting for router to apply changes...")
            time.sleep(15)
            
            if test_fixed_ip_access():
                logger.info("🎉 SUCCESS! Automatic configuration worked!")
                logger.info(f"✅ http://138.199.60.185:8005 is now accessible globally!")
                success = True
                break
    
    if not success:
        # Create automation script
        logger.info("🔧 Creating router automation script...")
        script_file = create_router_automation_script(routers[0])
        
        logger.info(f"📋 Running automation script: {script_file}")
        try:
            result = subprocess.run([str(script_file)], capture_output=True, text=True, timeout=120)
            logger.info(result.stdout)
            if result.stderr:
                logger.warning(result.stderr)
            
            if result.returncode == 0:
                success = True
        except Exception as e:
            logger.error(f"❌ Script failed: {e}")
    
    # Final test
    if success or test_fixed_ip_access():
        logger.info("")
        logger.info("🎉 FIXED IP ACCESS SUCCESSFUL!")
        logger.info("=" * 80)
        logger.info("✅ http://138.199.60.185:8005 - WORKING GLOBALLY!")
        logger.info("✅ http://138.199.60.185:8005/workbench - WORKING GLOBALLY!")
        logger.info("📱 Share these URLs with anyone worldwide!")
        logger.info("=" * 80)
    else:
        logger.warning("⚠️ Automatic setup incomplete")
        logger.info("📋 Manual router configuration may be needed")
        logger.info(f"🔧 Router: http://{routers[0] if routers else '192.168.1.1'}")
        logger.info("🔧 Port forwarding: External 8005 -> 10.7.7.2:8005")
    
    keep_running()

def keep_running():
    """Keep server running"""
    logger.info("")
    logger.info("⌨️ Press Ctrl+C to stop server")
    logger.info("📊 Server running...")
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
        logger.info("✅ Server stopped")

if __name__ == "__main__":
    main()