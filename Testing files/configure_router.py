#!/usr/bin/env python3
"""
Router Configuration Helper for NGINX + IP Setup
Helps configure port forwarding for HTTPS access
"""

import subprocess
import requests
import logging
import webbrowser
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def detect_router_info():
    """Detect router IP and local IP information"""
    
    # Get router IP
    try:
        result = subprocess.run(['route', '-n', 'get', 'default'], 
                              capture_output=True, text=True)
        router_ip = None
        for line in result.stdout.split('\n'):
            if 'gateway:' in line:
                router_ip = line.split(':')[1].strip()
                break
        
        if not router_ip:
            # Alternative method
            result = subprocess.run(['netstat', '-rn'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'default' in line and 'en0' in line:
                    parts = line.split()
                    if len(parts) > 1 and '.' in parts[1]:
                        router_ip = parts[1]
                        break
        
        if not router_ip:
            router_ip = "172.20.10.1"  # From your netstat output
            
    except Exception as e:
        logger.error(f"Failed to detect router IP: {e}")
        router_ip = "172.20.10.1"  # Fallback to detected IP
    
    # Get local IP
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "10.7.7.2"  # Your known local IP
    
    return router_ip, local_ip

def test_router_access(router_ip):
    """Test if router admin panel is accessible"""
    try:
        response = requests.get(f'http://{router_ip}', timeout=5)
        return True
    except:
        return False

def open_router_admin(router_ip):
    """Open router admin panel in browser"""
    try:
        webbrowser.open(f'http://{router_ip}')
        logger.info(f"✅ Router admin panel opened: http://{router_ip}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to open browser: {e}")
        return False

def display_port_forwarding_guide(router_ip, local_ip):
    """Display detailed port forwarding guide"""
    
    logger.info("")
    logger.info("🔧 ROUTER PORT FORWARDING CONFIGURATION")
    logger.info("=" * 80)
    logger.info(f"📍 Router IP: {router_ip}")
    logger.info(f"📍 Your Computer IP: {local_ip}")
    logger.info(f"📍 Your Public IP: 138.199.60.185")
    logger.info("")
    
    logger.info("📋 STEP-BY-STEP CONFIGURATION:")
    logger.info("")
    logger.info("1. 🌐 ROUTER ADMIN ACCESS:")
    logger.info(f"   • URL: http://{router_ip}")
    logger.info("   • Look for login credentials on router label/sticker")
    logger.info("   • Common defaults: admin/admin, admin/password, admin/(blank)")
    logger.info("")
    
    logger.info("2. 🔍 FIND PORT FORWARDING MENU:")
    logger.info("   Look for these menu items:")
    logger.info("   • 'Port Forwarding'")
    logger.info("   • 'Virtual Server'")
    logger.info("   • 'NAT Forwarding'")
    logger.info("   • 'Applications & Gaming'")
    logger.info("   • 'Advanced Settings' → 'Port Forwarding'")
    logger.info("")
    
    logger.info("3. ➕ ADD TWO PORT FORWARDING RULES:")
    logger.info("")
    logger.info("   📋 RULE 1 - HTTP (Port 80):")
    logger.info("   • Service Name: 'Robeco HTTP'")
    logger.info("   • External Port: 80")
    logger.info(f"   • Internal IP: {local_ip}")
    logger.info("   • Internal Port: 80")
    logger.info("   • Protocol: TCP")
    logger.info("")
    logger.info("   📋 RULE 2 - HTTPS (Port 443):")
    logger.info("   • Service Name: 'Robeco HTTPS'")
    logger.info("   • External Port: 443")
    logger.info(f"   • Internal IP: {local_ip}")
    logger.info("   • Internal Port: 443")
    logger.info("   • Protocol: TCP")
    logger.info("")
    
    logger.info("4. 💾 SAVE CONFIGURATION:")
    logger.info("   • Click 'Save' or 'Apply'")
    logger.info("   • Some routers require restart")
    logger.info("   • Wait 2-3 minutes for changes to take effect")
    logger.info("")
    
    logger.info("🎯 RESULT AFTER CONFIGURATION:")
    logger.info("   • HTTP access: http://138.199.60.185 → redirects to HTTPS")
    logger.info("   • HTTPS access: https://138.199.60.185 → your Robeco app")
    logger.info("   • Global access from ANY computer worldwide")
    logger.info("")
    
    logger.info("⚠️  COMMON ROUTER BRANDS & MENU LOCATIONS:")
    logger.info("   • TP-Link: Advanced → NAT Forwarding → Virtual Servers")
    logger.info("   • Netgear: Dynamic DNS → Port Forwarding / Port Triggering")
    logger.info("   • Linksys: Smart Wi-Fi Tools → Port Forwarding")
    logger.info("   • ASUS: Adaptive QoS → Traditional QoS → Port Forwarding")
    logger.info("   • D-Link: Advanced → Port Forwarding")
    logger.info("")
    logger.info("=" * 80)

def check_ports_open():
    """Check if ports 80 and 443 are available locally"""
    import socket
    
    ports_status = {}
    
    for port in [80, 443]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                ports_status[port] = "Available"
        except OSError as e:
            if e.errno == 48:  # Address already in use
                ports_status[port] = "In use"
            elif e.errno == 13:  # Permission denied
                ports_status[port] = "Needs sudo"
            else:
                ports_status[port] = f"Error: {e}"
    
    logger.info("🔍 Port Status Check:")
    for port, status in ports_status.items():
        if status == "Available":
            logger.info(f"   ✅ Port {port}: {status}")
        elif status == "Needs sudo":
            logger.info(f"   ⚠️ Port {port}: {status} (normal for system ports)")
        else:
            logger.info(f"   ❌ Port {port}: {status}")
    
    return ports_status

def main():
    """Main router configuration helper"""
    
    logger.info("🌐 Router Configuration Helper for NGINX Setup")
    logger.info("🎯 Goal: Enable access via https://138.199.60.185")
    logger.info("")
    
    # Detect network information
    router_ip, local_ip = detect_router_info()
    logger.info(f"📍 Detected Router IP: {router_ip}")
    logger.info(f"📍 Detected Your Computer IP: {local_ip}")
    logger.info("")
    
    # Check port availability
    ports_status = check_ports_open()
    logger.info("")
    
    # Test router access
    logger.info("🔍 Testing router accessibility...")
    if test_router_access(router_ip):
        logger.info(f"✅ Router is accessible at http://{router_ip}")
        
        # Try to open router admin panel
        logger.info("🌐 Opening router admin panel...")
        open_router_admin(router_ip)
        
    else:
        logger.warning(f"⚠️ Router may not be accessible at http://{router_ip}")
        logger.info("💡 Common router IPs to try manually:")
        for ip in ['192.168.1.1', '192.168.0.1', '10.0.0.1', '172.20.10.1']:
            logger.info(f"   • http://{ip}")
    
    # Display configuration guide
    display_port_forwarding_guide(router_ip, local_ip)
    
    logger.info("")
    logger.info("🚀 After router configuration:")
    logger.info("   1. Start nginx: sudo nginx")
    logger.info("   2. Start Robeco: python run_professional_system.py")
    logger.info("   3. Test: https://138.199.60.185")
    logger.info("")
    logger.info("💡 Need help? The router admin panel should be open in your browser!")

if __name__ == "__main__":
    main()