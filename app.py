from flask import Flask
from pywebio.platform.flask import webio_view
from pywebio.input import *
from pywebio.output import *
from pywebio.session import set_env, register_thread, run_js
from datetime import datetime
import threading
import time

app = Flask(__name__)
messages = []
clients = {}  # Store username and their last seen message index

def scroll_to_bottom():
    """Function to scroll to bottom of messages"""
    run_js("""
        var messagesDiv = document.getElementById('messages');
        if (messagesDiv) {
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            // Add smooth scroll behavior
            messagesDiv.style.scrollBehavior = 'smooth';
            
            // Check if user is near bottom before auto-scrolling
            var isNearBottom = messagesDiv.scrollHeight - messagesDiv.scrollTop - messagesDiv.clientHeight < 100;
            if (isNearBottom) {
                setTimeout(function() {
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }, 100);
            }
        }
    """)

def update_messages(username, last_msg_idx):
    """Update messages display only if there are new messages"""
    current_msg_count = len(messages)
    
    if current_msg_count > last_msg_idx:
        with use_scope('messages', clear=True):
            for message in messages[-50:]:
                is_user_message = message['username'] == username
                class_name = 'user-message' if is_user_message else 'other-message'
                align_style = 'margin-left: 20%;' if is_user_message else 'margin-right: 20%;'
                
                put_html(f'''
                    <div class="message {class_name}" style="{align_style}">
                        <div class="username">{message['username']}</div>
                        <div class="message-text">{message['text']}</div>
                        <div class="timestamp">{message['time']}</div>
                    </div>
                ''')
        scroll_to_bottom()
        return current_msg_count
    return last_msg_idx

def message_updater(username):
    """Background thread to update messages"""
    last_msg_idx = 0
    while True:
        last_msg_idx = update_messages(username, last_msg_idx)
        time.sleep(0.5)

def chat_app():
    global messages, clients
    
    username = input("Enter your username:", required=True)
    clients[username] = 0
    
    set_env(title=f"Chat - {username}")
    
    put_html("""
    <style>
        .chat-container { 
            max-width: 800px;
            margin: 0 auto;
            padding: 10px;
        }
        .header {
            margin-bottom: 10px;
        }
        .messages-container {
            height: 400px;
            overflow-y: auto;
            padding: 10px;
            background: #fafafa;
            border-radius: 5px;
            border: 1px solid #dee2e6;
            margin-bottom: 10px;
            scroll-behavior: smooth;
        }
        .message {
            margin: 5px 0;
            padding: 8px;
            border-radius: 8px;
            max-width: 75%;
            word-wrap: break-word;
            animation: fadeIn 0.3s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user-message {
            background: #e3f2fd;
            color: #000;
        }
        .other-message {
            background: #85c5e5;
            color: white;
        }
        .timestamp { 
            font-size: 0.75em; 
            color: #666;
            margin-top: 4px;
        }
        .username { 
            font-weight: bold; 
            margin-bottom: 3px;
        }
        .message-text {
            margin: 4px 0;
            line-height: 1.4;
        }
        input[type="text"] {
            padding: 8px 12px;
            border-radius: 4px;
            border: 1px solid #ddd;
            width: 100%;
            margin-top: 10px;
        }
    </style>
    <div class="chat-container">
    """)
    
    with use_scope('main'):
        put_html('<div class="header">')
        put_markdown("## Chat Room")
        put_markdown(f"Connected as: **{username}**")
        put_html('</div>')
        put_html('<div class="messages-container" id="messages"></div>')
        scroll_to_bottom()

    # Start message updater in a separate thread
    updater = threading.Thread(target=message_updater, args=(username,))
    updater.daemon = True
    register_thread(updater)
    updater.start()
    
    while True:
        try:
            msg = input("", type=TEXT, placeholder="Type your message here...")
            if msg is not None and msg.strip():
                messages.append({
                    'username': username,
                    'text': msg,
                    'time': datetime.now().strftime("%I:%M %p")
                })
                if len(messages) > 100:
                    messages.pop(0)
                scroll_to_bottom()  # Scroll after sending a message
        except:
            if username in clients:
                del clients[username]
            break

app.add_url_rule('/', 'webio_view', webio_view(chat_app), methods=['GET', 'POST', 'OPTIONS'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
