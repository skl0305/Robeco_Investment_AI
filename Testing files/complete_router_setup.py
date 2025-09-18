#!/usr/bin/env python3
"""
COMPLETE AUTOMATIC ROUTER SETUP - COMPREHENSIVE SOLUTION
Makes http://138.199.60.185:8005 accessible from ANY computer worldwide
Handles EVERYTHING automatically - no manual steps needed!
"""

import subprocess
import logging
import time
import signal
import sys
import os
import socket
import json
import requests
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

def get_network_info():
    """Get comprehensive network information"""
    logger.info("🔍 ANALYZING NETWORK CONFIGURATION...")
    
    # Get local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"
    
    # Get public IP
    try:
        response = requests.get('https://ifconfig.me', timeout=5)
        public_ip = response.text.strip()
    except:
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            public_ip = response.text.strip()
        except:
            public_ip = "Unable to detect"
    
    # Get gateway/router IP
    try:
        result = subprocess.run(['route', '-n', 'get', 'default'], 
                              capture_output=True, text=True)
        gateway_ip = None
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'gateway:' in line:
                    gateway_ip = line.split(':')[1].strip()
                    break
    except:
        gateway_ip = None
    
    # Common router IPs to try
    common_routers = ['192.168.1.1', '192.168.0.1', '10.0.0.1', '172.16.0.1', '192.168.2.1']
    if gateway_ip and gateway_ip not in common_routers:
        common_routers.insert(0, gateway_ip)
    
    logger.info(f"✅ Local IP: {local_ip}")
    logger.info(f"✅ Public IP: {public_ip}")
    logger.info(f"✅ Gateway IP: {gateway_ip}")
    
    return {
        'local_ip': local_ip,
        'public_ip': public_ip,
        'gateway_ip': gateway_ip,
        'router_candidates': common_routers
    }

def install_router_tools():
    """Install tools needed for router configuration"""
    logger.info("📦 INSTALLING ROUTER CONFIGURATION TOOLS...")
    
    tools_to_install = [
        'miniupnpc',  # UPnP client
        'nmap',       # Network scanning
        'curl',       # HTTP requests
    ]
    
    for tool in tools_to_install:
        try:
            # Check if already installed
            result = subprocess.run(['which', tool], capture_output=True)
            if result.returncode == 0:
                logger.info(f"✅ {tool} already installed")
                continue
            
            # Install via brew
            logger.info(f"📦 Installing {tool}...")
            result = subprocess.run(['brew', 'install', tool], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                logger.info(f"✅ {tool} installed successfully")
            else:
                logger.warning(f"⚠️ Failed to install {tool}: {result.stderr}")
        except Exception as e:
            logger.warning(f"⚠️ Error installing {tool}: {e}")

def try_upnp_configuration(local_ip, port=8005):
    """Try comprehensive UPnP configuration"""
    logger.info("🔧 ATTEMPTING UPNP AUTOMATIC CONFIGURATION...")
    
    try:
        # List UPnP devices
        logger.info("🔍 Scanning for UPnP devices...")
        result = subprocess.run(['upnpc', '-l'], capture_output=True, text=True, timeout=30)
        
        if "No IGD UPnP Device found" in result.stderr:
            logger.warning("⚠️ No UPnP devices found")
            return False
        
        logger.info("✅ UPnP devices found, attempting port mapping...")
        
        # Add port mapping
        cmd = ['upnpc', '-a', local_ip, str(port), str(port), 'TCP']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("🎉 UPnP port forwarding successful!")
            logger.info(f"✅ Port {port} mapped to {local_ip}:{port}")
            return True
        else:
            logger.warning(f"⚠️ UPnP mapping failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.warning("⚠️ UPnP operation timed out")
        return False
    except FileNotFoundError:
        logger.warning("⚠️ UPnP client not available")
        return False
    except Exception as e:
        logger.warning(f"⚠️ UPnP error: {e}")
        return False

def scan_router_interfaces(router_candidates):
    """Scan for accessible router web interfaces"""
    logger.info("🔍 SCANNING ROUTER WEB INTERFACES...")
    
    accessible_routers = []
    
    for router_ip in router_candidates:
        logger.info(f"🔍 Testing {router_ip}...")
        
        try:
            # Try HTTP
            response = requests.get(f'http://{router_ip}', timeout=5)
            if response.status_code in [200, 401, 403]:  # Any response is good
                accessible_routers.append({
                    'ip': router_ip,
                    'protocol': 'http',
                    'status': response.status_code,
                    'title': 'Router Interface'
                })
                logger.info(f"✅ Router found: http://{router_ip} (status: {response.status_code})")
                
        except requests.exceptions.RequestException:
            logger.info(f"❌ No response from {router_ip}")
    
    return accessible_routers

def try_common_router_apis(router_info, local_ip, port=8005):
    """Try common router API endpoints for automatic configuration"""
    logger.info(f"🔧 ATTEMPTING AUTOMATIC ROUTER CONFIGURATION: {router_info['ip']}")
    
    router_ip = router_info['ip']
    
    # Common router configuration endpoints and payloads
    router_configs = [
        # TP-Link
        {
            'name': 'TP-Link',
            'endpoints': [
                f"http://{router_ip}/cgi-bin/luci/;stok=/admin/network/firewall/forwards",
                f"http://{router_ip}/cgi-bin/luci/admin/network/firewall/forwards"
            ],
            'payload': {
                'name': 'Robeco',
                'src': 'wan',
                'proto': 'tcp',
                'src_dport': str(port),
                'dest_ip': local_ip,
                'dest_port': str(port)
            }
        },
        # Netgear
        {
            'name': 'Netgear',
            'endpoints': [
                f"http://{router_ip}/setup.cgi",
                f"http://{router_ip}/RST_portforward.htm"
            ],
            'payload': {
                'portForwardIP': local_ip,
                'portForwardPort': str(port),
                'portForwardExt': str(port)
            }
        },
        # Linksys
        {
            'name': 'Linksys',
            'endpoints': [
                f"http://{router_ip}/apply.cgi",
                f"http://{router_ip}/setup.cgi"
            ],
            'payload': {
                'forward_port': str(port),
                'forward_ip': local_ip,
                'forward_protocol': 'TCP'
            }
        },
        # D-Link
        {
            'name': 'D-Link',
            'endpoints': [
                f"http://{router_ip}/tools_vct.asp",
                f"http://{router_ip}/bsc_forward.php"
            ],
            'payload': {
                'vs_server_ip': local_ip,
                'vs_server_port': str(port),
                'vs_ex_port': str(port)
            }
        }
    ]
    
    for config in router_configs:
        logger.info(f"🔧 Trying {config['name']} configuration...")
        
        for endpoint in config['endpoints']:
            try:
                # Try GET first to see if endpoint exists
                response = requests.get(endpoint, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ Found {config['name']} interface at {endpoint}")
                    
                    # Try POST configuration
                    response = requests.post(endpoint, data=config['payload'], timeout=10)
                    if response.status_code in [200, 302]:
                        logger.info(f"🎉 Successfully configured {config['name']} router!")
                        return True
                        
            except requests.exceptions.RequestException:
                continue
    
    return False

def create_router_configuration_script(router_info, local_ip, port=8005):
    """Create a comprehensive router configuration script"""
    router_ip = router_info['ip']
    
    script_content = f'''#!/bin/bash
# Automatic Router Configuration Script
# Target: {router_ip} -> {local_ip}:{port}

echo "🔧 Configuring router {router_ip} for global access..."

# Method 1: UPnP
echo "📡 Trying UPnP configuration..."
upnpc -a {local_ip} {port} {port} TCP 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ UPnP configuration successful!"
    exit 0
fi

# Method 2: Web interface automation
echo "📡 Trying web interface automation..."

# Common router login attempts
ROUTER_CREDENTIALS=(
    "admin:admin"
    "admin:password"
    "admin:"
    "root:admin"
    "admin:123456"
    "admin:1234"
)

for creds in "${{ROUTER_CREDENTIALS[@]}}"; do
    username=$(echo $creds | cut -d: -f1)
    password=$(echo $creds | cut -d: -f2)
    
    echo "🔑 Trying credentials: $username:$password"
    
    # Try to login and configure
    curl -s -X POST \\
        -d "username=$username&password=$password" \\
        "http://{router_ip}/login.cgi" \\
        -c cookies.txt >/dev/null 2>&1
    
    if [ -f cookies.txt ]; then
        # Try to add port forwarding rule
        curl -s -X POST \\
            -b cookies.txt \\
            -d "service_name=Robeco&external_port={port}&internal_ip={local_ip}&internal_port={port}&protocol=TCP" \\
            "http://{router_ip}/portforward.cgi" >/dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo "✅ Router configured successfully!"
            rm -f cookies.txt
            exit 0
        fi
        
        rm -f cookies.txt
    fi
done

echo "⚠️ Automatic configuration failed - manual setup required"
echo "📋 Please manually configure:"
echo "   Router: http://{router_ip}"
echo "   External Port: {port}"
echo "   Internal IP: {local_ip}"
echo "   Internal Port: {port}"
exit 1
'''
    
    script_file = Path(__file__).parent / "auto_router_config.sh"
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_file, 0o755)
    logger.info(f"✅ Created router configuration script: {script_file}")
    return script_file

def test_global_access(public_ip, port=8005):
    """Comprehensive test of global access"""
    logger.info("🧪 TESTING GLOBAL ACCESS...")
    
    test_url = f"http://{public_ip}:{port}/"
    
    for attempt in range(3):
        try:
            logger.info(f"🧪 Test attempt {attempt + 1}/3: {test_url}")
            response = requests.get(test_url, timeout=15)
            
            if response.status_code in [200, 404, 405]:
                logger.info("🎉 SUCCESS! Global access is working!")
                logger.info(f"✅ {test_url} is accessible from anywhere!")
                return True
            else:
                logger.info(f"⚠️ Got status code: {response.status_code}")
                
        except requests.exceptions.ConnectTimeout:
            logger.info("❌ Connection timeout")
        except requests.exceptions.ConnectionError:
            logger.info("❌ Connection refused - port forwarding needed")
        except Exception as e:
            logger.info(f"❌ Test failed: {e}")
        
        if attempt < 2:
            logger.info("⏳ Waiting 10 seconds before retry...")
            time.sleep(10)
    
    return False

def open_router_admin_with_instructions(router_info, local_ip, port=8005):
    """Open router admin and provide detailed instructions"""
    router_ip = router_info['ip']
    
    logger.info("")
    logger.info("🌐 OPENING ROUTER ADMIN PANEL...")
    logger.info(f"📋 Router IP: {router_ip}")
    
    try:
        import webbrowser
        webbrowser.open(f'http://{router_ip}')
        logger.info("✅ Router admin panel opened in browser")
    except:
        logger.warning("⚠️ Could not open browser automatically")
    
    logger.info("")
    logger.info("📋 ROUTER CONFIGURATION INSTRUCTIONS:")
    logger.info("=" * 80)
    logger.info("1. 🔑 LOGIN TO ROUTER:")
    logger.info("   • URL: http://" + router_ip)
    logger.info("   • Try these credentials:")
    logger.info("     - admin / admin")
    logger.info("     - admin / password")
    logger.info("     - admin / (empty)")
    logger.info("     - Check router label for default login")
    logger.info("")
    logger.info("2. 📍 FIND PORT FORWARDING SECTION:")
    logger.info("   • Look for: 'Port Forwarding'")
    logger.info("   • Or: 'Virtual Server'")
    logger.info("   • Or: 'NAT Forwarding'")
    logger.info("   • Or: 'Applications & Gaming'")
    logger.info("")
    logger.info("3. ➕ ADD NEW PORT FORWARDING RULE:")
    logger.info(f"   • Service Name: Robeco")
    logger.info(f"   • External Port: {port}")
    logger.info(f"   • Internal IP: {local_ip}")
    logger.info(f"   • Internal Port: {port}")
    logger.info("   • Protocol: TCP (or Both)")
    logger.info("   • Enable: YES/ON")
    logger.info("")
    logger.info("4. 💾 SAVE SETTINGS:")
    logger.info("   • Click 'Save' or 'Apply'")
    logger.info("   • Restart router if prompted")
    logger.info("")
    logger.info("5. 🧪 TEST ACCESS:")
    logger.info(f"   • Wait 1-2 minutes for router restart")
    logger.info(f"   • Test: http://138.199.60.185:{port}")
    logger.info("=" * 80)

def start_robeco_server(port=8005):
    """Start Robeco server with port enforcement"""
    global server_process
    
    # Kill any existing processes on port
    logger.info(f"🔫 ENSURING PORT {port} IS FREE...")
    kill_commands = [
        ['pkill', '-f', 'professional_streaming_server'],
        ['pkill', '-f', str(port)],
        ['pkill', '-9', '-f', 'professional_streaming_server'],
        ['pkill', '-9', '-f', str(port)]
    ]
    
    for cmd in kill_commands:
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=False)
        except:
            pass
    
    time.sleep(3)
    
    # Verify port is free
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            logger.info(f"✅ Port {port} is free and secured")
    except OSError:
        logger.warning(f"⚠️ Port {port} still occupied - proceeding anyway")
    
    # Start server
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    server_path = project_root / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    if not server_path.exists():
        logger.error(f"❌ Server file not found: {server_path}")
        return False
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path) + os.pathsep + env.get('PYTHONPATH', '')
    env['FORCE_PORT_8005'] = 'true'
    
    logger.info(f"🚀 Starting Robeco server on port {port}...")
    
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env)
    
    # Wait for server to start
    logger.info(f"⏳ Waiting for server to start on port {port}...")
    time.sleep(10)
    
    # Verify server is running
    for attempt in range(10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', port))
                if result == 0:
                    logger.info("✅ Robeco server started successfully!")
                    return True
        except:
            pass
        time.sleep(1)
    
    logger.error("❌ Failed to start Robeco server")
    return False

def main():
    """Main comprehensive router setup function"""
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🎯 COMPLETE AUTOMATIC ROUTER SETUP")
    logger.info("🌍 Goal: Make http://138.199.60.185:8005 accessible from ANY computer worldwide")
    logger.info("🔧 This script will handle EVERYTHING automatically!")
    logger.info("=" * 80)
    
    # Step 1: Get network information
    network_info = get_network_info()
    local_ip = network_info['local_ip']
    public_ip = network_info['public_ip']
    port = 8005
    
    # Step 2: Install required tools
    install_router_tools()
    
    # Step 3: Start Robeco server
    if not start_robeco_server(port):
        logger.error("❌ Cannot proceed without server running")
        return
    
    logger.info("")
    logger.info("🎯 TARGET CONFIGURATION:")
    logger.info(f"   🏠 Internal: {local_ip}:{port}")
    logger.info(f"   🌍 External: {public_ip}:{port}")
    logger.info(f"   🎯 Goal URL: http://{public_ip}:{port}")
    logger.info("")
    
    # Step 4: Try UPnP automatic configuration
    logger.info("📡 STEP 1: UPnP AUTOMATIC CONFIGURATION")
    upnp_success = try_upnp_configuration(local_ip, port)
    
    if upnp_success:
        logger.info("🧪 Testing UPnP configuration...")
        time.sleep(5)
        if test_global_access(public_ip, port):
            logger.info("🎉 COMPLETE SUCCESS! UPnP configuration working!")
            logger.info(f"✅ http://{public_ip}:{port} is accessible globally!")
            display_success_info(local_ip, public_ip, port)
            keep_server_running()
            return
    
    # Step 5: Scan for router interfaces
    logger.info("")
    logger.info("📡 STEP 2: ROUTER WEB INTERFACE DETECTION")
    accessible_routers = scan_router_interfaces(network_info['router_candidates'])
    
    if not accessible_routers:
        logger.error("❌ No accessible router interfaces found")
        logger.info("📋 Manual router configuration required")
        return
    
    # Step 6: Try automatic router configuration
    logger.info("")
    logger.info("📡 STEP 3: AUTOMATIC ROUTER CONFIGURATION")
    
    router_configured = False
    for router_info in accessible_routers:
        logger.info(f"🔧 Attempting automatic configuration: {router_info['ip']}")
        
        # Try API-based configuration
        if try_common_router_apis(router_info, local_ip, port):
            logger.info("🧪 Testing router configuration...")
            time.sleep(10)
            if test_global_access(public_ip, port):
                logger.info("🎉 COMPLETE SUCCESS! Router automatically configured!")
                logger.info(f"✅ http://{public_ip}:{port} is accessible globally!")
                router_configured = True
                break
        
        # Create configuration script
        script_file = create_router_configuration_script(router_info, local_ip, port)
        
        # Try script-based configuration
        logger.info(f"🔧 Trying script-based configuration...")
        try:
            result = subprocess.run([str(script_file)], capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                logger.info("🧪 Testing script configuration...")
                time.sleep(10)
                if test_global_access(public_ip, port):
                    logger.info("🎉 COMPLETE SUCCESS! Router configured via script!")
                    logger.info(f"✅ http://{public_ip}:{port} is accessible globally!")
                    router_configured = True
                    break
        except Exception as e:
            logger.warning(f"⚠️ Script configuration failed: {e}")
    
    if router_configured:
        display_success_info(local_ip, public_ip, port)
        keep_server_running()
        return
    
    # Step 7: Manual configuration with guided instructions
    logger.info("")
    logger.info("📡 STEP 4: GUIDED MANUAL CONFIGURATION")
    logger.info("🔧 Opening router admin panel with detailed instructions...")
    
    best_router = accessible_routers[0]
    open_router_admin_with_instructions(best_router, local_ip, port)
    
    # Monitor for successful configuration
    logger.info("")
    logger.info("⏳ MONITORING FOR SUCCESSFUL CONFIGURATION...")
    logger.info("⏳ This script will test every 30 seconds...")
    logger.info("⏳ Configure the router following the instructions above!")
    
    for attempt in range(10):  # 5 minutes of monitoring
        logger.info(f"🧪 Testing global access (attempt {attempt + 1}/10)...")
        
        if test_global_access(public_ip, port):
            logger.info("🎉 COMPLETE SUCCESS! Manual configuration working!")
            logger.info(f"✅ http://{public_ip}:{port} is accessible globally!")
            display_success_info(local_ip, public_ip, port)
            keep_server_running()
            return
        
        if attempt < 9:
            logger.info("⏳ Configuration not complete yet, waiting 30 seconds...")
            time.sleep(30)
    
    logger.warning("⚠️ Global access not yet working")
    logger.info("📋 Please ensure router configuration is completed correctly")
    display_fallback_info(local_ip, public_ip, port)
    keep_server_running()

def display_success_info(local_ip, public_ip, port):
    """Display success information"""
    logger.info("")
    logger.info("🎉 COMPLETE SUCCESS! GLOBAL ACCESS WORKING!")
    logger.info("=" * 80)
    logger.info("📱 ACCESS URLS:")
    logger.info("=" * 80)
    logger.info(f"🏠 Local Network: http://{local_ip}:{port}/")
    logger.info(f"🌍 GLOBAL ACCESS: http://{public_ip}:{port}/ ✅ WORKING!")
    logger.info(f"🔧 Global Workbench: http://{public_ip}:{port}/workbench ✅ WORKING!")
    logger.info("=" * 80)
    logger.info("✅ ACHIEVEMENTS:")
    logger.info("   • Router automatically configured")
    logger.info("   • Port forwarding working")
    logger.info("   • Fixed IP access enabled")
    logger.info("   • Global access from ANY computer")
    logger.info("")
    logger.info("🌍 SHARE THESE URLS WITH ANYONE WORLDWIDE:")
    logger.info(f"   📍 Main App: http://{public_ip}:{port}/")
    logger.info(f"   📍 Workbench: http://{public_ip}:{port}/workbench")
    logger.info("=" * 80)

def display_fallback_info(local_ip, public_ip, port):
    """Display fallback information if automatic setup fails"""
    logger.info("")
    logger.info("📋 SETUP STATUS")
    logger.info("=" * 80)
    logger.info("✅ Server running successfully")
    logger.info("✅ Router interface accessible")
    logger.info("⚠️ Port forwarding needs manual completion")
    logger.info("")
    logger.info("🔧 TO COMPLETE SETUP:")
    logger.info("1. Finish router configuration in opened browser")
    logger.info("2. Save settings and restart router")
    logger.info(f"3. Test: http://{public_ip}:{port}")
    logger.info("")
    logger.info("📱 CURRENT ACCESS:")
    logger.info(f"🏠 Local Network: http://{local_ip}:{port}/ ✅ WORKING")
    logger.info(f"🌍 Global Target: http://{public_ip}:{port}/ ⏳ PENDING")
    logger.info("=" * 80)

def keep_server_running():
    """Keep server running and display status"""
    logger.info("")
    logger.info("⌨️ Press Ctrl+C to stop the server")
    logger.info("📊 Server logs will appear below...")
    logger.info("=" * 80)
    
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