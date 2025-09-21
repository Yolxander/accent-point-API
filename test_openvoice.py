#!/usr/bin/env python3
"""
Test script to verify OpenVoice CLI installation
"""

def test_import():
    """Test if openvoice_cli can be imported correctly"""
    try:
        from openvoice_cli import tune_one
        print("✅ Successfully imported tune_one from openvoice_cli")
        return True
    except ImportError as e:
        print(f"❌ Failed to import tune_one: {e}")
        return False

def test_import_all():
    """Test if we can import other functions"""
    try:
        from openvoice_cli import tune_batch
        print("✅ Successfully imported tune_batch from openvoice_cli")
        return True
    except ImportError as e:
        print(f"❌ Failed to import tune_batch: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing OpenVoice CLI installation...")
    print("=" * 50)
    
    # Test main import
    main_import = test_import()
    
    # Test batch import
    batch_import = test_import_all()
    
    print("=" * 50)
    if main_import and batch_import:
        print("🎉 All imports successful! OpenVoice CLI is ready to use.")
    else:
        print("⚠️ Some imports failed. Check your installation.")
        print("\nTo install OpenVoice CLI:")
        print("pip install openvoice-cli")
