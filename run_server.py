import uvicorn
import sys
import os

# Ensure project root is in python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("Abhi Cloud Tech - Enterprise FinOps ML Web Server")
    print("=" * 65)
    print("Starting FastAPI Production Server...")
    print("Web Application URL: http://localhost:8000")
    print("Swagger API Docs:    http://localhost:8000/docs")
    print("=" * 65 + "\n")
    
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
