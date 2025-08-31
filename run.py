"""
Simple runner script to start the Fuel Tracker app
"""

import subprocess
import sys
import os
import streamlit as st
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
    """Check if Streamlit secrets are configured"""
    try:
        # Check if secrets.toml exists
        secrets_file = Path(".streamlit/secrets.toml")
        if not secrets_file.exists():
            print("❌ secrets.toml file not found")
            print("Please create a secrets.toml file with your Supabase credentials")
            return False
        
        # Try to access Streamlit secrets
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
        
        if not supabase_url or not supabase_key:
            print("❌ SUPABASE_URL or SUPABASE_KEY not set in secrets.toml")
            return False
        
        print("✅ Streamlit secrets are configured")
        return True
    except KeyError as e:
        print(f"❌ Missing secret: {e}")
        print("Please add SUPABASE_URL and SUPABASE_KEY to secrets.toml")
        return False
    except Exception as e:
        print(f"❌ Error loading secrets: {e}")
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