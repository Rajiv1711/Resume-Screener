import requests
import time
import subprocess
import sys
import os

def test_server():
    # Start the server in a subprocess
    print("Starting server...")
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app.main:app", 
        "--host", "127.0.0.1", "--port", "8000"
    ], cwd=os.getcwd())
    
    # Wait for server to start
    time.sleep(10)
    
    try:
        # Test the root endpoint
        response = requests.get("http://127.0.0.1:8000/", timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8000/health", timeout=30)
        print(f"Health Check: {response.json()}")
        
        print("Server is running correctly!")
        
    except requests.exceptions.ConnectionError:
        print("Server failed to start - connection refused")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Kill the process
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_server()