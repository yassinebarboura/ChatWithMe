from flask import Flask
from pywebio.platform.flask import webio_view
from pywebio.input import *
from pywebio.output import *
from pywebio.session import set_env, run_async
from datetime import datetime
import asyncio

app = Flask(__name__)

messages = []
clients = set()

async def chat_app():
    global messages, clients
    
    username = await input("Enter your username:", required=True)
    clients.add(username)
    
    set_env(title=f"Chat - {username}")
    
    await put_html("""
    <style>
        .chat-container { 
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .messages-container {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #fafafa;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 10px;
        }
        .user-message {
            background: #f0f0f0;
            margin-right: 20%;
        }
        .other-message {
            background: #85c5e5;
            margin-left: 20%;
            color: white;
        }
        .timestamp { font-size: 0.8em; color: #666; }
        .username { font-weight: bold; margin-bottom: 5px; }
    </style>
    <div class="chat-container">
    """)
    
    async with use_scope('main'):
        await put_markdown("## Chat Room")
        await put_markdown(f"Connected as: **{username}**")
        await put_html('<div class="messages-container" id="messages"></div>')
    
    update_task = None
    
    async def update_messages():
        last_count = 0
        try:
            while True:
                if len(messages) > last_count:
                    async with use_scope('messages', clear=True):
                        for msg in messages[-50:]:  # Show last 50 messages
                            class_name = 'user-message' if msg['username'] == username else 'other-message'
                            await put_html(f'''
                                <div class="message {class_name}">
                                    <div class="username">{msg['username']}</div>
                                    {msg['text']}
                                    <div class="timestamp">{msg['time']}</div>
                                </div>
                            ''')
                    last_count = len(messages)
                await asyncio.sleep(1)  # Reduced update frequency
        except asyncio.CancelledError:
            return

    try:
        update_task = asyncio.create_task(update_messages())
        
        while True:
            msg = await input_group("", [
                input(placeholder="Type your message here...", name="msg")
            ])
            
            if msg and msg["msg"].strip():
                messages.append({
                    'username': username,
                    'text': msg["msg"],
                    'time': datetime.now().strftime("%I:%M %p")
                })
                if len(messages) > 100:  # Keep only last 100 messages
                    messages.pop(0)
                
    except Exception as e:
        print(f"Chat error: {e}")
    finally:
        if update_task:
            update_task.cancel()
            try:
                await update_task
            except asyncio.CancelledError:
                pass
        clients.remove(username)

app.add_url_rule('/', 'webio_view', webio_view(chat_app), methods=['GET', 'POST', 'OPTIONS'])

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)