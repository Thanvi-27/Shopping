#!/usr/bin/env python
"""
🚀 START HERE - Complete Shop Analytics System Setup

This script guides you through the entire setup process
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}".ljust(70))
    print("="*70 + "\n")

def print_step(num, text):
    """Print numbered step"""
    print(f"\n⚡ STEP {num}: {text}")
    print("-" * 70)

def run_command(cmd, description):
    """Run a command and show progress"""
    print(f"\n   Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ {description} complete")
            return True
        else:
            print(f"   ❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main setup flow"""
    print_header("SHOP ANALYTICS SYSTEM - COMPLETE SETUP GUIDE")
    
    base_path = Path(__file__).parent
    
    print("""
    This is a 100% Python customer analytics system that includes:
    ✓ Streamlit dashboard (graphical interface)
    ✓ OpenCV camera detection
    ✓ SQLite database
    ✓ Real-time analytics
    
    Total setup time: ~2-5 minutes
    """)
    
    # Step 1: Check Python
    print_step(1, "VERIFY PYTHON INSTALLATION")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")
    
    if sys.version_info < (3, 8):
        print("\n   ❌ Python 3.8+ required. Please upgrade Python.")
        return 1
    
    print("   ✅ Python version OK")
    
    # Step 2: Create virtual environment
    print_step(2, "CREATE VIRTUAL ENVIRONMENT (OPTIONAL)")
    venv_path = base_path / 'venv'
    
    if not venv_path.exists():
        response = input("\n   Create virtual environment? (y/n): ").lower()
        if response == 'y':
            if run_command(f'"{sys.executable}" -m venv venv', "Virtual environment created"):
                print(f"\n   📍 Activate with:")
                print(f"      Windows: venv\\Scripts\\activate")
                print(f"      macOS/Linux: source venv/bin/activate")
            else:
                print("   ⚠️  Manual setup may be needed")
    else:
        print("   ✅ Virtual environment already exists")
    
    # Step 3: Install dependencies
    print_step(3, "INSTALL PYTHON DEPENDENCIES")
    print(f"\n   Required packages:")
    print(f"   • streamlit (dashboard UI)")
    print(f"   • plotly (interactive charts)")
    print(f"   • pandas (data processing)")
    print(f"   • opencv-python (computer vision)")
    print(f"   • numpy (numerical computing)")
    
    response = input("\n   Install dependencies? (y/n): ").lower()
    if response == 'y':
        if run_command(f'"{sys.executable}" -m pip install -r requirements.txt', 
                      "Dependencies installed"):
            print("\n   ✅ All packages installed")
        else:
            print("\n   ⚠️  Some packages failed to install")
            print("   This might be a network issue. Try again later.")
    
    # Step 4: Verify installation
    print_step(4, "VERIFY INSTALLATION")
    response = input("\n   Run verification script? (y/n): ").lower()
    if response == 'y':
        run_command(f'"{sys.executable}" verify.py', "Verification complete")
    
    # Step 5: Setup demo data
    print_step(5, "INITIALIZE DATABASE WITH DEMO DATA")
    print(f"\n   This will create:")
    print(f"   • SQLite database (shop_analytics.db)")
    print(f"   • Demo user account (demo/demo123)")
    print(f"   • 4 sample shop zones")
    print(f"   • 2 sample cameras")
    print(f"   • 7 days of sample customer data")
    
    response = input("\n   Setup demo data? (y/n): ").lower()
    if response == 'y':
        if run_command(f'"{sys.executable}" setup.py', "Demo data setup"):
            print("\n   ✅ Database ready!")
        else:
            print("\n   ⚠️  Setup failed - manual setup may be needed")
    
    # Step 6: Run dashboard
    print_step(6, "START THE DASHBOARD")
    print(f"\n   Ready to launch Streamlit dashboard!")
    print(f"\n   The dashboard will open automatically at: http://localhost:8501")
    
    response = input("\n   Start dashboard now? (y/n): ").lower()
    if response == 'y':
        print(f"\n   🚀 Launching dashboard...")
        print(f"   (Press Ctrl+C to stop)\n")
        
        try:
            # Change to app directory and run
            os.chdir(base_path)
            subprocess.run(f'"{sys.executable}" -m streamlit run app/app.py', shell=True)
        except KeyboardInterrupt:
            print("\n\n   ✅ Dashboard stopped")
        except Exception as e:
            print(f"\n   ❌ Error: {e}")
    
    # Final summary
    print_header("SETUP COMPLETE!")
    
    print("""
    📊 NEXT STEPS:
    
    1. LOGIN TO DASHBOARD
       • Username: demo
       • Password: demo123
    
    2. EXPLORE FEATURES
       • Dashboard - View real-time metrics
       • Analytics - Filter and export data
       • Cameras - Add/manage RTSP cameras
       • Zones - Define shop sections
    
    3. TRY EXAMPLES
       • Run: python examples.py
       • See 7 different usage examples
    
    4. CUSTOMIZE FOR YOUR SHOP
       • Add your camera RTSP URLs
       • Define your shop zones
       • Start tracking customers!
    
    📚 DOCUMENTATION:
       • README.md - Full reference
       • QUICKSTART.md - 5-minute guide
       • SUMMARY.md - Project overview
       • examples.py - Code examples
    
    ✅ READY TO RUN:
       streamlit run app/app.py
    """)
    
    return 0

if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        exit(1)
