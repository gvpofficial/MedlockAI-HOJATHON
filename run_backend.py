import os
import sys
import uvicorn

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print(f"Starting MedLock AI Backend from: {backend_dir}")
    print("API available at http://localhost:8000 (Swagger: http://localhost:8000/docs)")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        app_dir=backend_dir,
        reload=False
    )
