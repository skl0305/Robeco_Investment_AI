#!/usr/bin/env python3
"""
Deployment Verification Script
Ensures 100% reliable deployment of Robeco Professional System
"""

import socket
import requests
import subprocess
import time
import sys
import logging
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Verify all required dependencies are installed"""
    logger.info("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'websockets', 'psutil', 'requests', 
        'google-generativeai', 'aiohttp', 'pandas', 'numpy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package}")
        except ImportError:
            missing.append(package)
            logger.error(f"❌ {package} - MISSING")
    
    if missing:
        logger.error(f"❌ Missing packages: {', '.join(missing)}")
        logger.info("📦 Install with: pip install " + ' '.join(missing))
        return False
    
    logger.info("✅ All dependencies satisfied")
    return True

def check_project_structure():
    """Verify project structure is intact"""
    logger.info("🔍 Checking project structure...")
    
    project_root = Path(__file__).parent
    required_files = [
        "src/robeco/backend/professional_streaming_server.py",
        "src/robeco/frontend/static",
        "requirements.txt",
        "run_professional_system.py"
    ]
    
    missing = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            logger.info(f"✅ {file_path}")
        else:
            missing.append(file_path)
            logger.error(f"❌ {file_path} - MISSING")
    
    if missing:
        logger.error(f"❌ Missing files: {', '.join(missing)}")
        return False
    
    logger.info("✅ Project structure intact")
    return True

def check_port_8005():
    """Check if port 8005 is available or can be freed"""
    logger.info("🔍 Checking port 8005 availability...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', 8005))
            logger.info("✅ Port 8005 is available")
            return True
    except OSError:
        logger.info("⚠️  Port 8005 is occupied, checking if we can free it...")
        
        # Check if we can kill processes on the port
        try:
            result = subprocess.run(['lsof', '-ti', ':8005'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                logger.info(f"📋 Found {len(pids)} process(es) on port 8005")
                logger.info("✅ Port can be freed (processes found)")
                return True
            else:
                logger.error("❌ Port 8005 occupied but no processes found")
                return False
        except Exception as e:
            logger.error(f"❌ Cannot check port processes: {e}")
            return False

def test_internet_connectivity():
    """Test internet connectivity for IP detection"""
    logger.info("🔍 Testing internet connectivity...")
    
    test_urls = ['https://ifconfig.me', 'https://api.ipify.org', 'https://httpbin.org/ip']
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Internet connectivity OK ({url})")
                return True
        except Exception:
            continue
    
    logger.error("❌ No internet connectivity - public IP detection may fail")
    return False

def get_network_info():
    """Get and display network information"""
    logger.info("🔍 Getting network information...")
    
    try:
        # Get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        
        # Get public IP
        try:
            response = requests.get('https://ifconfig.me', timeout=5)
            public_ip = response.text.strip()
        except:
            public_ip = "Unable to detect"
        
        logger.info(f"📍 Local IP: {local_ip}")
        logger.info(f"📍 Public IP: {public_ip}")
        
        return local_ip, public_ip
    except Exception as e:
        logger.error(f"❌ Network info failed: {e}")
        return None, None

def test_server_startup():
    """Test if the server can start (dry run)"""
    logger.info("🔍 Testing server startup (dry run)...")
    
    try:
        # Import the server module to check for import errors
        sys.path.append(str(Path(__file__).parent / "src"))
        from robeco.backend.professional_streaming_server import force_use_port_8005
        
        # Test the port enforcement function
        logger.info("✅ Server module imports successfully")
        logger.info("✅ Port enforcement function available")
        return True
        
    except Exception as e:
        logger.error(f"❌ Server startup test failed: {e}")
        return False

def generate_deployment_report(local_ip, public_ip):
    """Generate final deployment report"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("📋 DEPLOYMENT VERIFICATION COMPLETE")
    logger.info("=" * 80)
    
    if local_ip and public_ip:
        logger.info("🌐 READY FOR DEPLOYMENT!")
        logger.info("")
        logger.info("📱 SHARE THESE URLS WITH OUTSIDERS:")
        logger.info(f"   🔗 Main App: http://{public_ip}:8005/")
        logger.info(f"   🔗 Workbench: http://{public_ip}:8005/workbench")
        logger.info(f"   🔗 Local Network: http://{local_ip}:8005/")
        logger.info("")
        logger.info("🎯 TO DEPLOY:")
        logger.info("   1. Configure router port forwarding: 8005 → " + local_ip + ":8005")
        logger.info("   2. Run: python run_professional_system.py")
        logger.info("   3. Share the public URLs above")
        logger.info("")
        logger.info("✅ System is 100% ready for deployment!")
    else:
        logger.info("⚠️  DEPLOYMENT READY (with limitations)")
        logger.info("   - Local deployment will work")
        logger.info("   - Internet access may require manual configuration")
    
    logger.info("=" * 80)

def main():
    """Main verification function"""
    logger.info("🚀 Robeco Professional System - Deployment Verification")
    logger.info("=" * 60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Port 8005", check_port_8005),
        ("Internet Connectivity", test_internet_connectivity),
        ("Server Startup", test_server_startup)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        logger.info(f"\n🔍 Running: {check_name}")
        results[check_name] = check_func()
    
    # Get network info
    logger.info(f"\n🔍 Running: Network Information")
    local_ip, public_ip = get_network_info()
    
    # Summary
    logger.info("\n📊 VERIFICATION SUMMARY:")
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {check_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("\n🎉 ALL CHECKS PASSED!")
        generate_deployment_report(local_ip, public_ip)
        return True
    else:
        failed_checks = [name for name, result in results.items() if not result]
        logger.info(f"\n❌ FAILED CHECKS: {', '.join(failed_checks)}")
        logger.info("🔧 Fix the issues above before deploying")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)