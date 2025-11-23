#!/usr/bin/env python3
"""
Initialize configuration system to create default settings file.
"""

import sys
import os

# Add the current directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.config import config_manager
    
    print("[FIX] Initializing configuration system...")
    
    # Load configuration (this will create default file if it doesn't exist)
    config = config_manager.get_config()
    
    print("[PASS] Configuration loaded successfully!")
    print(f"📁 Config file location: {config_manager.config_file}")
    
    # Display some default settings
    print("\n[INFO] Default Settings:")
    print(f"Graphics: {config.graphics.resolution_width}x{config.graphics.resolution_height}")
    print(f"Audio Volume: {config.audio.master_volume}")
    print(f"Player Name: {config.player_profile.name}")
    print(f"Difficulty: {config.difficulty.difficulty_level}")
    
    # Save configuration to ensure file is created
    if config_manager.save_config():
        print("[PASS] Configuration saved successfully!")
    else:
        print("[FAIL] Failed to save configuration")
    
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    print("Make sure you're running this from the TurboShells root directory")
except Exception as e:
    print(f"[FAIL] Error: {e}")
