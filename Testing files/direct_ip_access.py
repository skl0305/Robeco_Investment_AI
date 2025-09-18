#!/usr/bin/env python3
"""
Direct IP Access for Robeco - SIMPLE SOLUTION
Run Robeco directly on port 8080 for global access
"""

import subprocess
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def kill_processes_on_ports():
    """Kill any processes on ports 8005, 8080, 8011"""
    ports = [8005, 8080, 8011]
    
    for port in ports:
        try:
            # Use lsof to find and kill processes
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(['kill', '-9', pid], check=False)
                        logger.info(f"🔫 Killed process {pid} on port {port}")
        except:
            pass

def modify_server_for_port_8080():
    """Modify the server to run on port 8080"""
    
    server_path = Path(__file__).parent / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    if not server_path.exists():
        logger.error(f"❌ Server file not found: {server_path}")
        return False
    
    try:
        # Read the server file
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Modify the port in the main function
        if 'if __name__ == "__main__":' in content:
            # Find and replace the uvicorn.run call
            new_content = content.replace(
                'uvicorn.run(app, host="0.0.0.0", port=port)',
                'uvicorn.run(app, host="0.0.0.0", port=8080)'
            )
            
            # Also modify the force_use_port function if it exists
            new_content = new_content.replace(
                'def force_use_port_8005():',
                'def force_use_port_8080():'
            )
            new_content = new_content.replace(
                'port = 8005',
                'port = 8080'
            )
            new_content = new_content.replace(
                'port = force_use_port_8005()',
                'port = 8080'
            )
            
            # Write back the modified content
            with open(server_path, 'w') as f:
                f.write(new_content)
            
            logger.info("✅ Modified server to use port 8080")
            return True
        else:
            logger.error("❌ Could not find main function in server file")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to modify server: {e}")
        return False

def start_robeco_on_8080():
    """Start Robeco directly on port 8080"""
    
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    server_path = project_root / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path) + os.pathsep + env.get('PYTHONPATH', '')
    
    logger.info("🚀 Starting Robeco server directly on port 8080...")
    
    # Start server
    process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env)
    
    return process

def display_success_info():
    """Display success information"""
    logger.info("")
    logger.info("🎉 ROBECO DIRECT IP ACCESS - SUCCESS!")
    logger.info("=" * 80)
    logger.info("📍 FIXED URL ACCESS:")
    logger.info("=" * 80)
    logger.info("🏠 Local: http://localhost:8080")
    logger.info("🏠 Network: http://10.7.7.2:8080")
    logger.info("🌍 GLOBAL: http://138.199.60.185:8080")
    logger.info("🔧 Workbench: http://138.199.60.185:8080/workbench")
    logger.info("=" * 80)
    logger.info("")
    logger.info("✅ BENEFITS:")
    logger.info("   • Fixed IP URL: http://138.199.60.185:8080")
    logger.info("   • Works from ANY computer worldwide")
    logger.info("   • No domain needed - just your IP!")
    logger.info("   • No complex proxy setup")
    logger.info("   • Direct server access")
    logger.info("")
    logger.info("🌐 TO ENABLE GLOBAL ACCESS:")
    logger.info("   1. Configure router port forwarding:")
    logger.info("      • External Port: 8080")
    logger.info("      • Internal IP: 10.7.7.2")
    logger.info("      • Internal Port: 8080")
    logger.info("      • Protocol: TCP")
    logger.info("")
    logger.info("   2. Router login: http://172.20.10.1")
    logger.info("      • Find 'Port Forwarding' or 'Virtual Server'")
    logger.info("      • Add the rule above")
    logger.info("      • Save and restart router")
    logger.info("")
    logger.info("🎯 RESULT: http://138.199.60.185:8080 works globally!")
    logger.info("=" * 80)

def main():
    """Main function"""
    
    logger.info("🌐 Direct IP Access Setup for Robeco")
    logger.info("🎯 Running Robeco directly on port 8080 for global access")
    logger.info("")
    
    # Kill any existing processes
    logger.info("🧹 Cleaning up existing processes...")
    kill_processes_on_ports()
    
    # Modify server to use port 8080
    logger.info("🔧 Configuring server for port 8080...")
    if not modify_server_for_port_8080():
        logger.error("❌ Failed to configure server")
        return
    
    # Start server
    process = start_robeco_on_8080()
    
    # Display information
    display_success_info()
    
    logger.info("⌨️  Press Ctrl+C to stop server")
    logger.info("📊 Server logs will appear below...")
    logger.info("=" * 80)
    
    # Wait for process
    try:
        process.wait()
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        logger.info("✅ Server stopped")

if __name__ == "__main__":
    main()