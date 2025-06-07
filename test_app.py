#!/usr/bin/env python3
"""Test script to run Flask app with better error handling"""

import sys
import traceback

try:
    from app import create_app
    
    print("Creating Flask app...")
    app = create_app()
    
    print("Starting Flask app on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    
except Exception as e:
    print(f"ERROR: Failed to start Flask app")
    print(f"Exception: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)