"""
Verification script - Test if all components are working
Run this to ensure everything is properly installed
"""

import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️  Warning: Python 3.8+ recommended")
        return False
    return True

def check_imports():
    """Check if all required packages are importable"""
    packages = {
        'streamlit': 'Streamlit',
        'plotly': 'Plotly',
        'pandas': 'Pandas',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
    }
    
    missing = []
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - NOT INSTALLED")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    return True

def check_database():
    """Check if database module works"""
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'app'))
        from database import init_db, get_connection
        
        init_db()
        conn = get_connection()
        
        # Test query
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM users')
        count = c.fetchone()[0]
        conn.close()
        
        print(f"✓ Database initialized ({count} users)")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def check_analytics():
    """Check if analytics module works"""
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'app'))
        from analytics import get_dashboard_summary
        
        # This should work with empty data
        summary = get_dashboard_summary('TEST')
        print(f"✓ Analytics module working")
        return True
    except Exception as e:
        print(f"✗ Analytics error: {e}")
        return False

def check_camera_processor():
    """Check if camera processor works"""
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'app'))
        from camera_processor import CustomerDetector
        
        detector = CustomerDetector()
        print(f"✓ Camera processor initialized")
        return True
    except Exception as e:
        print(f"✗ Camera processor error: {e}")
        return False

def check_streamlit():
    """Check if Streamlit app can be parsed"""
    try:
        app_path = Path(__file__).parent / 'app' / 'app.py'
        with open(app_path, 'r') as f:
            code = f.read()
        
        if 'streamlit' in code and 'st.title' in code:
            print(f"✓ Streamlit app configured ({len(code)} bytes)")
            return True
        else:
            print(f"✗ Streamlit app structure invalid")
            return False
    except Exception as e:
        print(f"✗ Streamlit app error: {e}")
        return False

def check_files():
    """Check if all required files exist"""
    required_files = [
        'app/app.py',
        'app/database.py',
        'app/analytics.py',
        'app/camera_processor.py',
        'requirements.txt',
        'setup.py',
        'README.md',
    ]
    
    base_path = Path(__file__).parent
    missing = []
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✓ {file_path} ({size} bytes)")
        else:
            print(f"✗ {file_path} - NOT FOUND")
            missing.append(file_path)
    
    return len(missing) == 0

def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("   SHOP ANALYTICS SYSTEM - VERIFICATION".center(60))
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_imports),
        ("Project Files", check_files),
        ("Database Module", check_database),
        ("Analytics Module", check_analytics),
        ("Camera Processor", check_camera_processor),
        ("Streamlit App", check_streamlit),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("   VERIFICATION SUMMARY".center(60))
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print("\n✅ ALL CHECKS PASSED! System is ready to use.\n")
        print("Next steps:")
        print("  1. Run: python setup.py")
        print("  2. Run: streamlit run app/app.py")
        print("  3. Login with: demo / demo123")
        print("\n" + "="*60 + "\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed.\n")
        print("To fix:")
        print("  1. Check the error messages above")
        print("  2. Run: pip install -r requirements.txt")
        print("  3. Run verification again: python verify.py")
        print("\n" + "="*60 + "\n")
        return 1

if __name__ == '__main__':
    exit(main())
