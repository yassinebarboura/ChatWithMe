from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import set_env
from datetime import datetime
import time
import socket
import sys
import signal

def find_free_port(start_port=8000, max_port=9000):
    """Find a free port between start_port and max_port."""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None         

def signal_handler(sig, frame):
    print("\nShutting down gracefully...")
    sys.exit(0)

def chat_app():
    set_env(title="Live Chat Support")
    
    # Styling
    put_html("""
    <style>
        .chat-container { 
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #fff;
        }
        .customer-info {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 10px;
        }
        .agent-message {
            background: #85c5e5;
            margin-left: 20%;
            color: white;
        }
        .user-message {
            background: #f0f0f0;
            margin-right: 20%;
        }
        .timestamp {
            font-size: 0.8em;
            color: #666;
        }
        .input-area {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
        }
    </style>
    """)

    # Header
    put_html('<div class="chat-container">')
    
    # Customer info section
    put_html('''
        <div class="customer-info">
            <h3>Chloe Smith</h3>
            <p>Email: chloe@example.com</p>
            <p>Location: Sydney, Australia</p>
        </div>
    ''')

    # Chat messages
    def add_message(text, is_agent=False):
        current_time = datetime.now().strftime("%I:%M %p")
        class_name = "agent-message" if is_agent else "user-message"
        put_html(f'''
            <div class="message {class_name}">
                {text}
                <div class="timestamp">{current_time}</div>
            </div>
        ''')

    # Initial messages
    add_message("Do you have a trial version available?", False)
    time.sleep(1)
    
    add_message("Unfortunately we do not have a trial or demo that you can install on your own server. "
                "We also don't have a demo installation setup on our own servers. We feel that it is best "
                "for customers to try the software on their own server or hosting account to ensure that "
                "everything functions as expected and is suited to their existing configuration.", True)

    # Chat input
    while True:
        try:
            msg = input_group("", [
                input(placeholder="Type your message here...", name="msg")
            ])
            
            if msg and msg["msg"]:
                add_message(msg["msg"], False)
                time.sleep(1)
                add_message("Thank you for your message. An agent will respond shortly.", True)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error in chat: {e}")
            break

def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Find an available port
        port = find_free_port()
        if port is None:
            print("Error: Could not find an available port")
            sys.exit(1)
            
        print(f"\nStarting chat server on http://127.0.0.1:{port}")
        print("Press Ctrl+C to stop the server")
        
        start_server(
            applications=chat_app,
            port=port,
            debug=True,
            host='0.0.0.0',
            cdn=False,
            auto_open_webbrowser=True
        )
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)