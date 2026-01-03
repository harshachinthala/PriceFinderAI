import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import start_app

if __name__ == "__main__":
    print("Starting PriceFinder AI...")
    app = start_app()
    app.launch(inbrowser=True)
