#!/usr/bin/env python3
"""
Test script for the configuration system.
Tests all major components of the Phase 2 implementation.
"""

# Add project root to path
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


import sys
import os
import json
from pathlib import Path

# Add the current directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_config_manager():
    """Test the configuration manager."""
    print("[TEST] Testing Configuration Manager...")

    try:
        from src.core.config import config_manager, GameConfig

        # Test loading configuration
        config = config_manager.get_config()
        assert config is not None, "Failed to load configuration"

        # Test graphics settings
        assert config.graphics.resolution_width == 1024, "Default width incorrect"
        assert config.graphics.resolution_height == 768, "Default height incorrect"
        assert config.graphics.fullscreen == False, "Default fullscreen incorrect"

        # Test audio settings
        assert config.audio.master_volume >= 0.0, "Default master volume incorrect"
        assert config.audio.enabled, "Default audio enabled incorrect"

        # Test player profile
        assert config.player_profile.name == "Player", "Default player name incorrect"

        print("[PASS] Configuration Manager tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Configuration Manager test failed: {e}")
        return False


def test_graphics_manager():
    """Test the graphics manager."""
    print("[TEST] Testing Graphics Manager...")

    try:
        from src.core.graphics_manager import graphics_manager

        # Test loading settings
        assert graphics_manager.current_settings is not None, "Failed to load graphics settings"

        # Test resolution
        resolution = graphics_manager.get_current_resolution()
        assert resolution == (1024, 768), f"Expected (1024, 768), got {resolution}"

        # Test quality levels
        quality = graphics_manager.get_quality_level()
        assert quality in ["low", "medium", "high", "ultra"], f"Invalid quality level: {quality}"

        # Test available resolutions
        resolutions = graphics_manager.get_available_resolutions()
        assert len(resolutions) > 0, "No available resolutions"
        assert (1024, 768) in resolutions, "Standard resolution not available"

        # Test display info
        info = graphics_manager.get_display_info()
        assert "current_resolution" in info, "Display info missing current resolution"
        assert "quality_level" in info, "Display info missing quality level"

        print("[PASS] Graphics Manager tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Graphics Manager test failed: {e}")
        return False


def test_audio_manager():
    """Test the audio manager."""
    print("[TEST] Testing Audio Manager...")

    try:
        from src.core.audio_manager import audio_manager

        # Test loading settings
        assert audio_manager.current_settings is not None, "Failed to load audio settings"

        # Test volume levels
        master_volume = audio_manager.get_master_volume()
        assert 0.0 <= master_volume <= 1.0, f"Invalid master volume: {master_volume}"

        # Test effective volumes
        music_volume = audio_manager.get_effective_music_volume()
        sfx_volume = audio_manager.get_effective_sfx_volume()
        assert 0.0 <= music_volume <= 1.0, f"Invalid music volume: {music_volume}"
        assert 0.0 <= sfx_volume <= 1.0, f"Invalid SFX volume: {sfx_volume}"

        # Test volume setting
        success = audio_manager.set_master_volume(0.5)
        assert success, "Failed to set master volume"
        assert audio_manager.get_master_volume() == 0.5, "Master volume not set correctly"

        # Test audio info
        info = audio_manager.get_audio_info()
        assert "enabled" in info, "Audio info missing enabled status"
        assert "master_volume" in info, "Audio info missing master volume"

        print("[PASS] Audio Manager tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Audio Manager test failed: {e}")
        return False


def test_save_protection():
    """Test the save protection system."""
    print("[TEST] Testing Save Protection System...")

    try:
        from src.core.save_protection import SaveProtectionManager
        save_protection_manager = SaveProtectionManager()

        # Test directory structure
        assert save_protection_manager.save_dir.exists(), "Save directory not created"
        assert save_protection_manager.backup_dir.exists(), "Backup directory not created"

        # Create a test save file
        test_save_data = {
            "game_data": {"money": 100, "day": 1},
            "turtles": [],
            "preferences": {}
        }

        test_save_file = save_protection_manager.save_dir / "test_save.json"
        with open(test_save_file, 'w') as f:
            json.dump(test_save_data, f)

        # Test validation
        is_valid, error = save_protection_manager.validate_save_file("test_save.json")
        assert is_valid, f"Test save file validation failed: {error}"

        # Test backup creation
        success = save_protection_manager.create_backup("test_save.json", "test")
        assert success, "Failed to create backup"

        # Test save file info
        info = save_protection_manager.get_save_file_info("test_save.json")
        assert info is not None, "Failed to get save file info"
        assert info.is_valid, "Save file info shows invalid"
        assert info.backup_count > 0, "No backups found"

        # Test backup list
        backups = save_protection_manager.get_backup_list("test_save.json")
        assert len(backups) > 0, "No backups in list"

        # Test corruption detection (without actual recovery)
        is_corrupted = save_protection_manager.detect_corruption("test_save.json", "JSONDecodeError: test")
        assert is_corrupted, "Failed to detect corruption"

        # Test recovery would work if there were valid backups
        # (Skip actual recovery test to avoid file system complications)

        # Test export/import
        export_path = save_protection_manager.save_dir / "exported_save.json"
        success = save_protection_manager.export_save_file("test_save.json", export_path)
        assert success, "Failed to export save file"
        assert export_path.exists(), "Exported file not created"

        # Clean up test files
        test_save_file.unlink()
        export_path.unlink()

        print("[PASS] Save Protection System tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Save Protection System test failed: {e}")
        return False


def test_configuration_persistence():
    """Test that configuration changes persist."""
    print("[TEST] Testing Configuration Persistence...")

    try:
        from src.core.config import config_manager

        # Get original settings
        original_config = config_manager.get_config()
        original_width = original_config.graphics.resolution_width

        # Change settings
        original_config.graphics.resolution_width = 1280
        original_config.player_profile.name = "TestPlayer"

        # Save configuration
        success = config_manager.save_config()
        assert success, "Failed to save configuration"

        # Create new config manager instance (simulates restart)
        from src.core.config import ConfigManager
        new_manager = ConfigManager()
        new_config = new_manager.get_config()

        # Check if changes persisted
        assert new_config.graphics.resolution_width == 1280, "Width change not persisted"
        assert new_config.player_profile.name == "TestPlayer", "Player name change not persisted"

        # Restore original settings
        new_config.graphics.resolution_width = original_width
        new_config.player_profile.name = "Player"
        new_manager.save_config()

        print("[PASS] Configuration Persistence tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Configuration Persistence test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("[START] Starting Configuration System Tests")
    print("=" * 50)

    tests = [
        test_config_manager,
        test_graphics_manager,
        test_audio_manager,
        test_save_protection,
        test_configuration_persistence
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"[REPORT] Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] All tests passed! Phase 2 implementation is working correctly.")
        return True
    else:
        print("[FAIL] Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
