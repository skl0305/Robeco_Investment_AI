"""
Global primary API key loader for all AI services
Ensures ALL AI calls use the same primary key from file
"""
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_primary_api_key() -> str:
    """
    Load primary API key from file - used by ALL AI services
    Returns the current primary key from primary_gemini_key.txt
    """
    try:
        primary_key_file = Path(__file__).parent.parent / "backend" / "api_key" / "primary_gemini_key.txt"
        
        if os.path.exists(primary_key_file):
            with open(primary_key_file, 'r') as f:
                key = f.read().strip()
                if key:
                    logger.info(f"✅ Loaded primary API key: {key[:8]}...")
                    return key
        
        logger.error(f"❌ Primary key file not found: {primary_key_file}")
        raise FileNotFoundError("Primary API key file not found")
        
    except Exception as e:
        logger.error(f"❌ Error loading primary API key: {e}")
        raise

def get_backup_keys() -> list:
    """Load backup keys from pool file"""
    try:
        backup_file = Path(__file__).parent.parent / "backend" / "api_key" / "gemini_api_keys.txt"
        keys = []
        
        if os.path.exists(backup_file):
            with open(backup_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        keys.append(line)
        
        logger.info(f"✅ Loaded {len(keys)} backup keys")
        return keys
        
    except Exception as e:
        logger.error(f"❌ Error loading backup keys: {e}")
        return []