import sys
import os

# Add the project root to the python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import create_gradio_interface

if __name__ == "__main__":
    print("Starting PriceFinder AI...")
    
    # Create the Gradio interface
    app = create_gradio_interface()
    
    # Launch with Hugging Face compatible settings
    app.launch(
        server_name="0.0.0.0",  # Bind to all interfaces for Hugging Face
        server_port=7860,        # Default Gradio port
        share=False,             # Not needed on Hugging Face
        show_error=True          # Show errors for debugging
    )
