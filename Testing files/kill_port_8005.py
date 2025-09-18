#!/usr/bin/env python3
"""
🔫 PORT 8005 KILLER
Quick utility to kill any process using port 8005
"""

import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def kill_port_8005():
    """Kill any process using port 8005"""
    logger.info("🔫 KILLING ALL PROCESSES ON PORT 8005...")
    
    # Method 1: Kill by process name
    kill_commands = [
        ['pkill', '-9', '-f', 'professional_streaming_server'],
        ['pkill', '-9', '-f', '8005'],
        ['pkill', '-9', '-f', 'uvicorn.*8005'],
        ['pkill', '-9', '-f', 'python.*8005'],
        ['pkill', '-9', '-f', 'FINAL_SOLUTION'],
        ['pkill', '-9', '-f', 'run_professional_system']
    ]
    
    for cmd in kill_commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                logger.info(f"✅ Killed processes: {' '.join(cmd)}")
        except:
            pass
    
    # Method 2: Kill by port using lsof
    try:
        result = subprocess.run(['lsof', '-ti:8005'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    try:
                        subprocess.run(['kill', '-9', pid], check=False)
                        logger.info(f"🔫 Killed PID {pid} on port 8005")
                    except:
                        pass
    except:
        pass
    
    # Method 3: Alternative port killing
    try:
        subprocess.run(['fuser', '-k', '8005/tcp'], capture_output=True, check=False)
    except:
        pass
    
    time.sleep(3)  # Wait for cleanup
    
    # Verify port is free
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 8005))
            logger.info("✅ Port 8005 is now FREE!")
            return True
    except OSError:
        logger.warning("⚠️ Port 8005 still occupied")
        return False

if __name__ == "__main__":
    success = kill_port_8005()
    if success:
        print("✅ Port 8005 successfully freed!")
    else:
        print("⚠️ Port 8005 still occupied - may need manual intervention")