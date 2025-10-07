#!/usr/bin/env python3
"""
Simple server startup script that should stay running
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "xray-medical-backend"
sys.path.insert(0, str(backend_dir))

# Change to the backend directory
os.chdir(backend_dir)

# Now import and run the server
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print("🏥 Starting X-ray Analysis Server with Gemini AI...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("🤖 Using real Gemini AI for analysis")
    print("Press Ctrl+C to stop the server\n")
    
    # Run the server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True
    )