"""
Simple runner script to start the Fuel Tracker app
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import streamlit
        import supabase
        import plotly
        import pandas
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment variables are set"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please copy .env.example to .env and add your Supabase credentials")
        return False
    
    # Try to load and check env vars
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
            print("❌ SUPABASE_URL or SUPABASE_KEY not set in .env file")
            return False
        
        print("✅ Environment variables are set")
        return True
    except Exception as e:
        print(f"❌ Error loading environment: {e}")
        return False

def run_app():
    """Run the Streamlit app"""
    if not check_requirements():
        return
    
    if not check_environment():
        return
    
    print("🚀 Starting Fuel Tracker...")
    print("📱 The app will open in your browser")
    print("💡 Use Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Fuel Tracker stopped")

if __name__ == "__main__":
    run_app()