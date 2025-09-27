#!/usr/bin/env python3
"""
Simple script to add new API keys to the Robeco system
Usage: python add_api_key.py "your-new-api-key-here"
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    if len(sys.argv) != 2:
        print("Usage: python add_api_key.py 'your-new-api-key-here'")
        print("Example: python add_api_key.py 'AIzaSyABC123...XYZ789'")
        return
    
    new_key = sys.argv[1].strip()
    
    try:
        from robeco.backend.api_key.gemini_api_key import add_api_key, get_api_key_stats
        
        print(f"🔑 Adding API key: {new_key[:8]}...{new_key[-4:]}")
        
        # Get current stats
        before_stats = get_api_key_stats()
        print(f"📊 Current keys: {before_stats['total_keys']}")
        
        # Add the key
        success = add_api_key(new_key)
        
        if success:
            after_stats = get_api_key_stats()
            print(f"✅ Successfully added key! Total keys: {after_stats['total_keys']}")
            print("💡 No restart needed - the system will use the new key immediately")
        else:
            print("❌ Failed to add key (invalid format or duplicate)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()