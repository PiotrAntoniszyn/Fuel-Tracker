"""
Deployment helper for Streamlit app
"""

import streamlit as st
import os
from pathlib import Path

def setup_streamlit_config():
    """Setup Streamlit configuration for deployment"""
    
    config_dir = Path.home() / ".streamlit"
    config_dir.mkdir(exist_ok=True)
    
    # Create config.toml
    config_content = """
[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#ff6b6b"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
"""
    
    config_file = config_dir / "config.toml"
    with open(config_file, "w") as f:
        f.write(config_content)
    
    # Create secrets.toml template
    secrets_content = """
# Copy your .env values here for Streamlit Cloud deployment
SUPABASE_URL = "your_supabase_url_here"
SUPABASE_KEY = "your_supabase_anon_key_here"
"""
    
    secrets_file = config_dir / "secrets.toml"
    if not secrets_file.exists():
        with open(secrets_file, "w") as f:
            f.write(secrets_content)
        print(f"Created {secrets_file} - please update with your credentials")

if __name__ == "__main__":
    setup_streamlit_config()
    print("Streamlit configuration created!")
    print("Next steps:")
    print("1. Update ~/.streamlit/secrets.toml with your Supabase credentials")
    print("2. Run: streamlit run app.py")
    print("3. For Streamlit Cloud: push to GitHub and connect your repository")