"""CareerLens AI - Application Launcher.
Starts the FastAPI server and serves the reactive dashboard.
"""

import sys
import os
import webbrowser
import uvicorn

# Suppress minor warnings for clean console output
os.environ["PYTHONWARNINGS"] = "ignore"

def main():
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    url = f"http://{host}:{port}"

    print("=" * 65)
    print("   CareerLens AI [Target] - AI Career & Mock Interview Agent")
    print(f"   Server running at: {url}")
    print("   Open this URL in your web browser to start.")
    print("=" * 65)

    # Automatically launch default web browser after short delay
    if "--no-browser" not in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    uvicorn.run("backend.main:app", host=host, port=port, reload=False, log_level="info")

if __name__ == "__main__":
    main()
