#!/usr/bin/env python3
"""
Simple test script for Speak-to-LLM project structure.
"""

import os
import sys

def test_project_structure():
    """Test that project structure is correct."""
    print("🧪 Testing project structure...")
    
    # Current working directory should be the project root
    base_dir = os.getcwd()
    
    # Check key directories exist
    required_dirs = [
        'src',
        'src/stt',
        'src/tts', 
        'src/llm',
        'src/utils',
        'examples',
        'tests',
        'docs'
    ]
    
    all_passed = True
    
    for dir_path in required_dirs:
        full_path = os.path.join(base_dir, dir_path)
        if os.path.exists(full_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Missing directory: {dir_path}")
            all_passed = False
    
    # Check key files exist
    required_files = [
        'README.md',
        'requirements.txt',
        'package.json',
        '.env.example',
        'src/__init__.py',
        'main.py'
    ]
    
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
            all_passed = False
    
    return all_passed

def test_imports():
    """Test basic imports."""
    print("\n🧪 Testing imports...")
    
    # Add src to path - use current directory
    sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
    
    try:
        from utils.config import Config
        print("✅ Config import successful")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from utils.audio_utils import AudioUtils
        print("✅ AudioUtils import successful")
    except Exception as e:
        print(f"❌ AudioUtils import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration."""
    print("\n🧪 Testing configuration...")
    
    sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
    
    try:
        from utils.config import Config
        
        config = Config()
        print("✅ Config initialization successful")
        
        # Test basic properties
        assert config.stt_config is not None
        assert config.tts_config is not None
        assert config.llm_config is not None
        assert config.audio_config is not None
        print("✅ Config properties available")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🎯 Speak-to-LLM Project Tests")
    print("=" * 40)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Basic Imports", test_imports),
        ("Configuration", test_config)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary")
    print("=" * 40)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())