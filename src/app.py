import gradio as gr
import sys
import os
from src.llm_engine import process_query
from src.rag_pipeline import initialize_vector_db

# Ensure the root directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def start_app():
    print("Initializing Knowledge Base...")
    initialize_vector_db()

    custom_css = """
    /* ===== GLOBAL BACKGROUND WITH FLOATING PARTICLES ===== */
    body {
        background: linear-gradient(135deg, #fef9e7 0%, #fef5e7 50%, #fdebd0 100%);
        color: #1e293b;
        overflow-x: hidden;
    }
    @keyframes floatParticles {
        0% { transform: translateY(0px); opacity: 0.7; }
        50% { transform: translateY(-20px); opacity: 1; }
        100% { transform: translateY(0px); opacity: 0.7; }
    }
    .particle {
        position: absolute;
        width: 8px;
        height: 8px;
        background: #f59e0b;
        border-radius: 50%;
        animation: floatParticles 6s infinite ease-in-out;
        opacity: 0.6;
    }

    /* Place multiple particles */
    #particle-1 { top: 15%; left: 20%; animation-delay: 0s; }
    #particle-2 { top: 30%; left: 70%; animation-delay: 1s; }
    #particle-3 { top: 60%; left: 40%; animation-delay: 2s; }
    #particle-4 { top: 75%; left: 85%; animation-delay: 3s; }
    #particle-5 { top: 50%; left: 10%; animation-delay: 4s; }

    /* ===== HEADER 3D ANIMATION ===== */
    #app-header {
        text-align: center;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.85) 0%, rgba(249, 115, 22, 0.85) 100%),
                    url('https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=1200&h=400&fit=crop') center/cover;
        background-blend-mode: overlay;
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 
            0 10px 30px rgba(59, 130, 246, 0.3),
            0 20px 60px rgba(249, 115, 22, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        position: relative;
    }
    
    #app-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.3) 0%, rgba(251, 146, 60, 0.3) 100%);
        border-radius: 20px;
        pointer-events: none;
    }
    
    #app-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 3.5rem;
        text-align: center;
        color: #ffffff;
        margin-bottom: 10px;
        position: relative;
        z-index: 1;
        text-shadow: 
            3px 3px 6px rgba(0, 0, 0, 0.8),
            0 0 30px rgba(255, 255, 255, 0.5);
    }

    #app-header h3 {
        color: #ffffff;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 0;
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
    }

    /* ===== EXAMPLE QUESTIONS LABEL ===== */
    .example-label {
        text-align: center;
        color: #78350f;
        font-size: 0.95rem;
        margin-bottom: 10px;
        font-weight: 600;
    }
    
    /* ===== EXAMPLE BUTTONS ===== */
    .example-btn {
        background: #ffffff !important;
        border-radius: 10px !important;
        border: 2px solid #fbbf24 !important;
        padding: 10px 16px !important;
        color: #78350f !important;
        transition: 0.3s;
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(245, 158, 11, 0.2);
        font-size: 0.9rem;
    }
    .example-btn:hover {
        background: #fbbf24 !important;
        color: #78350f !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4);
    }

    /* ===== SEARCH INPUT & BUTTON ===== */
    .search-container {
        max-width: 800px;
        margin: 30px auto;
        gap: 12px !important;
        filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.1));
    }
    
    .custom-input textarea, .custom-input input {
        background: #ffffff !important;
        border: 2px solid #d1d5db !important;
        color: #0f172a !important;
        padding: 16px 20px !important;
        border-radius: 14px !important;
        font-size: 1.05rem !important;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    .custom-input textarea::placeholder, .custom-input input::placeholder {
        color: #9ca3af !important;
        font-size: 1rem !important;
    }
    
    .custom-input textarea:focus, .custom-input input:focus {
        border: 2px solid #0ea5e9 !important;
        box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.15), 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        outline: none !important;
    }

    .search-btn {
        background: linear-gradient(135deg, #0ea5e9, #06b6d4) !important;
        border-radius: 14px !important;
        padding: 16px 32px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        border: none !important;
        color: white !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.35);
        min-width: 140px !important;
    }
    .search-btn:hover {
        background: linear-gradient(135deg, #0284c7, #0891b2) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(14, 165, 233, 0.45);
    }
    .search-btn:active {
        transform: translateY(0px);
    }

    /* ===== CHAT CONTAINER ===== */
    .chatbot-container {
        background: #ffffff;
        border: 2px solid #fbbf24;
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
        box-shadow: 
            0 8px 20px rgba(0, 0, 0, 0.1),
            0 16px 40px rgba(245, 158, 11, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
    }
    
    .chatbot-container .message {
        background: #fef9e7;
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
    }
    
    .chatbot-container .message.user {
        background: #fef3c7;
    }
    
    .chatbot-container .message.bot {
        background: #ffffff;
        border: 1px solid #fbbf24;
    }
    
    .chatbot-container h1, .chatbot-container h2, .chatbot-container h3 {
        color: #78350f !important;
    }
    
    .chatbot-container a {
        color: #d97706 !important;
    }
    
    .chatbot-container table {
        color: #1e293b !important;
    }
    
    /* ===== CLEAR CHAT BUTTON ===== */
    .clear-btn {
        background: linear-gradient(135deg, #f97316, #fb923c) !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border: none !important;
        color: white !important;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(249, 115, 22, 0.3);
        margin-bottom: 10px !important;
    }
    .clear-btn:hover {
        background: linear-gradient(135deg, #ea580c, #f97316) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4);
    }
    """

    with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:

        # Floating particles
        gr.HTML("""
            <div id="particle-1" class="particle"></div>
            <div id="particle-2" class="particle"></div>
            <div id="particle-3" class="particle"></div>
            <div id="particle-4" class="particle"></div>
            <div id="particle-5" class="particle"></div>
        """)

        with gr.Column(elem_id="app-header"):
            gr.Markdown("""
                # 🛍️ PriceFinder AI  
                ### Your Intelligent Shopping Companion
            """)

        # Example Questions with Label
        gr.Markdown("""
        <div style="text-align: center; margin-bottom: 25px;">
            <p class="example-label">💡 Try these example questions:</p>
            <button class="example-btn">Best price for iPhone 15 Pro Max</button>
            <button class="example-btn">Cheapest 4K Monitor under $500</button>
            <button class="example-btn">Where to buy Sony WH-1000XM5?</button>
            <button class="example-btn">Compare MacBook Air M3 prices</button>
        </div>
        """)

        # Modern Search Bar with Input + Button Side-by-Side
        with gr.Row(elem_classes=["search-container"]):
            user_input = gr.Textbox(
                placeholder="🔍 Search for a product, e.g., 'iPhone 15 price'...",
                label="",
                elem_classes=["custom-input"],
                scale=4,
                container=False
            )
            search_button = gr.Button("Search", elem_classes=["search-btn"], scale=1)

        # Chat Output with History using State
        chat_history = gr.State([])
        
        # Clear button above output
        clear_button = gr.Button("🗑️ Clear Chat", elem_classes=["clear-btn"], size="sm")
        
        output_box = gr.Markdown("", elem_classes=["chatbot-container"])
        
        # Chat handler function
        def chat_handler(message, history):
            if not message.strip():
                return history, format_chat_history(history)
            # Get response from LLM
            response = process_query(message)
            # Append to history
            history.append({"user": message, "bot": response})
            return history, format_chat_history(history)
        
        def format_chat_history(history):
            if not history:
                return ""
            formatted = ""
            for exchange in history:
                formatted += f"**You:** {exchange['user']}\n\n"
                formatted += f"**PriceFinder AI:** {exchange['bot']}\n\n---\n\n"
            return formatted

        # Button click = call LLM
        search_button.click(
            fn=chat_handler,
            inputs=[user_input, chat_history],
            outputs=[chat_history, output_box]
        ).then(
            lambda: "",
            outputs=user_input
        )
        
        # Allow Enter key to submit
        user_input.submit(
            fn=chat_handler,
            inputs=[user_input, chat_history],
            outputs=[chat_history, output_box]
        ).then(
            lambda: "",
            outputs=user_input
        )
        
        # Clear chat button
        clear_button.click(
            fn=lambda: ([], ""),
            outputs=[chat_history, output_box]
        )

    return demo
