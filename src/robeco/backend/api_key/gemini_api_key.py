#!/usr/bin/env python3
"""
Robeco Gemini API Key Management
Centralized API key pool and intelligent rotation system - File-based loading
"""

import logging
import random
import os
from pathlib import Path
from typing import Tuple, Dict, Set, List, Optional

# Setup logging
logger = logging.getLogger(__name__)

# Pure rotation system - no suspension tracking

def load_api_keys_from_file() -> List[str]:
    """
    Load API keys from primary file first, then backup pool
    
    Returns:
        List[str]: List of API keys loaded from files
    """
    keys = []
    current_dir = Path(__file__).parent
    
    try:
        # FIRST: Load primary key
        primary_file = current_dir / "primary_gemini_key.txt"
        if primary_file.exists():
            with open(primary_file, 'r', encoding='utf-8') as f:
                primary_key = f.read().strip()
                if primary_key and primary_key.startswith('AIzaSy') and len(primary_key) == 39:
                    keys.append(primary_key)
                    logger.info(f"✅ Primary key loaded: {primary_key[:8]}...")
        
        # SECOND: Load backup pool
        backup_file = current_dir / "gemini_api_keys.txt"
        if backup_file.exists():
            with open(backup_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#') and line not in keys:
                        if line.startswith('AIzaSy') and len(line) == 39:
                            keys.append(line)
        
        logger.info(f"✅ Total keys loaded: {len(keys)} (primary + backup)")
        return keys
        
    except Exception as e:
        logger.error(f"❌ Error loading API keys: {e}")
        return []

def reload_api_keys() -> None:
    """
    Reload API keys from file - useful for adding new keys without restart
    """
    global api_keys
    new_keys = load_api_keys_from_file()
    if new_keys:
        api_keys.clear()
        api_keys.extend(new_keys)
        logger.info(f"🔄 Reloaded {len(api_keys)} API keys from file")
    else:
        logger.error("❌ Failed to reload API keys - keeping existing keys")

# Load API keys from file at module initialization
api_keys = load_api_keys_from_file()

# Fallback keys if file loading fails (to ensure system doesn't break)
if not api_keys:
    logger.warning("⚠️ Using fallback API keys - please update gemini_api_keys.txt")
    api_keys = [
        "AIzaSyAHWzUMMbRfEMuG1EzzNtWsSBPwyu150jQ",
        "AIzaSyDvzz4rn6LQEiEM2ZRnsoUPn-vEmgDJ174", 
        "AIzaSyBwxKQ2Mj-A0PEP3GhOg3QN6tSPoPvbZ0w"
    ]

# Global retry counter for key cycling
_key_retry_count = 0

def get_intelligent_api_key(*args, **kwargs) -> Optional[Tuple[str, Dict]]:
    """
    ROUND-ROBIN rotation system - cycles through all available keys to distribute load
    Automatically skips exhausted keys and resets them after timeout
    
    Returns:
        Tuple[str, Dict]: (selected_api_key, metadata_info)
    """
    global _key_retry_count
    
    # Check if we have any API keys at all
    if not api_keys:
        logger.error("❌ No API keys loaded! Check gemini_api_keys.txt file")
        return None
    
    agent_info = kwargs.get('agent_type', 'unknown')
    retry_attempt = kwargs.get('retry_attempt', 0)
    
    # True round-robin rotation through all keys
    key_index = _key_retry_count % len(api_keys)
    selected_key = api_keys[key_index]
    _key_retry_count += 1
    
    logger.info(f"🔄 Using key #{key_index} of {len(api_keys)} for {agent_info} (rotation #{_key_retry_count})")
    
    logger.info(f"🔍 API KEY DEBUG [{agent_info}]: selected_key={selected_key[:8]}...{selected_key[-4:]}, total_keys={len(api_keys)}")
    
    return selected_key, {
        "source": "round_robin", 
        "pool_size": len(api_keys), 
        "is_primary": (key_index == 0),
        "key_index": key_index,
        "rotation_count": _key_retry_count
    }

def suspend_api_key(api_key: str) -> None:
    """
    No-op function - primary key only system never suspends keys
    """
    logger.info(f"🔑 PRIMARY KEY ONLY system - always using primary key, no suspension: {api_key[:8]}...{api_key[-4:]}")

def reset_suspended_keys() -> None:
    """
    No-op function - primary key only system has no suspended keys
    """
    logger.info("🔑 PRIMARY KEY ONLY system - no suspended keys to reset, always using primary key")

def get_available_api_keys():
    """
    Returns all available API keys for rotation
    """
    return api_keys if api_keys else []

def get_api_key_stats() -> Dict:
    """
    Get current API key pool statistics
    
    Returns:
        Dict with total_keys count
    """
    return {
        "total_keys": len(api_keys),
        "available_keys": len(api_keys), 
        "suspended_keys": 0
    }

def add_api_key(new_key: str) -> bool:
    """
    Add a new API key to the pool and save to file
    
    Args:
        new_key: The new API key to add
        
    Returns:
        bool: True if successfully added, False otherwise
    """
    try:
        # Validate key format
        if not new_key.startswith('AIzaSy') or len(new_key) != 39:
            logger.error(f"❌ Invalid API key format: {new_key[:10]}...")
            return False
        
        # Check if key already exists
        if new_key in api_keys:
            logger.warning(f"⚠️ API key already exists: {new_key[:8]}...{new_key[-4:]}")
            return False
        
        # Add to memory
        api_keys.append(new_key)
        
        # Save to file
        current_dir = Path(__file__).parent
        keys_file = current_dir / "gemini_api_keys.txt"
        
        with open(keys_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{new_key}")
        
        logger.info(f"✅ Added new API key: {new_key[:8]}...{new_key[-4:]} (total: {len(api_keys)})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to add API key: {e}")
        return False