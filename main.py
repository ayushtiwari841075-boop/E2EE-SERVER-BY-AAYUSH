from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import sqlite3
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
import os
import time
import threading
import uuid
import urllib.parse
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'LORD_DEVIL_E2EE_2025_SECRET_KEY'

# Configuration
ADMIN_PASSWORD = "LORDXDEVILE2E2025"
WHATSAPP_NUMBER = "917668337116"
ADMIN_UID = "100003995292301"
APPROVAL_FILE = "approved_keys.json"
PENDING_FILE = "pending_approvals.json"

# Initialize database
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'users.db'

# HTML Templates
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>LORD DEVIL E2EE</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        * { font-family: 'Poppins', sans-serif; margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }
        .container { 
            background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); 
            padding: 40px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            border: 1px solid rgba(255,255,255,0.2); width: 400px; text-align: center;
        }
        .logo { width: 80px; height: 80px; border-radius: 50%; margin-bottom: 20px; border: 3px solid #4ecdc4; }
        h1 { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
        .tabs { display: flex; margin-bottom: 20px; }
        .tab { flex: 1; padding: 10px; background: rgba(255,255,255,0.1); border: none; color: white; cursor: pointer; }
        .tab.active { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); }
        input, textarea { 
            width: 100%; padding: 12px; margin: 8px 0; background: rgba(255,255,255,0.15); 
            border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; color: white;
        }
        input::placeholder { color: rgba(255,255,255,0.7); }
        button { 
            width: 100%; padding: 12px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
            border: none; border-radius: 8px; color: white; font-weight: bold; cursor: pointer; margin-top: 10px;
        }
        .message { padding: 10px; margin: 10px 0; border-radius: 8px; }
        .success { background: rgba(76, 175, 80, 0.3); color: #4caf50; }
        .error { background: rgba(244, 67, 54, 0.3); color: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <img src="https://i.postimg.cc/Pq1HGqZK/459c85fcaa5d9f0762479bf382225ac6.jpg" class="logo">
        <h1>LORD DEVIL E2EE</h1>
        <p style="color: rgba(255,255,255,0.8); margin-bottom: 20px;">seven billion smiles in his world but yours is my favourite</p>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('login')">LOGIN</button>
            <button class="tab" onclick="showTab('signup')">SIGN UP</button>
        </div>
        
        <div id="login-form">
            <form method="POST" action="/login">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">LOGIN</button>
            </form>
        </div>
        
        <div id="signup-form" style="display: none;">
            <form method="POST" action="/signup">
                <input type="text" name="username" placeholder="Choose Username" required>
                <input type="password" name="password" placeholder="Choose Password" required>
                <input type="password" name="confirm_password" placeholder="Confirm Password" required>
                <button type="submit">CREATE ACCOUNT</button>
            </form>
        </div>
        
        {% if message %}
        <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}
    </div>
    
    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('signup-form').style.display = 'none';
            
            if(tabName === 'login') {
                document.querySelector('.tab:nth-child(1)').classList.add('active');
                document.getElementById('login-form').style.display = 'block';
            } else {
                document.querySelector('.tab:nth-child(2)').classList.add('active');
                document.getElementById('signup-form').style.display = 'block';
            }
        }
    </script>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>E2EE Automation</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        * { font-family: 'Poppins', sans-serif; margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .header { 
            background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); 
            padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.2);
        }
        .logo { width: 80px; height: 80px; border-radius: 50%; margin-bottom: 15px; border: 3px solid #4ecdc4; }
        h1 { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .container { display: grid; grid-template-columns: 300px 1fr; gap: 20px; }
        .sidebar { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; }
        .main { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; }
        .tab { width: 100%; padding: 15px; margin: 5px 0; background: rgba(255,255,255,0.1); border: none; color: white; text-align: left; border-radius: 8px; }
        .tab.active { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); }
        input, textarea, select { 
            width: 100%; padding: 12px; margin: 8px 0; background: rgba(255,255,255,0.15); 
            border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; color: white;
        }
        button { 
            padding: 12px 25px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
            border: none; border-radius: 8px; color: white; font-weight: bold; cursor: pointer; margin: 5px;
        }
        .console { 
            background: rgba(0,0,0,0.7); color: #00ff88; padding: 15px; border-radius: 8px; 
            height: 300px; overflow-y: auto; font-family: monospace; margin-top: 20px;
        }
        .metric { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <img src="https://i.postimg.cc/Pq1HGqZK/459c85fcaa5d9f0762479bf382225ac6.jpg" class="logo">
        <h1>R0W3DY E2E OFFLINE</h1>
        <p style="color: rgba(255,255,255,0.8);">Welcome, {{ username }}! | Key: {{ user_key }}</p>
    </div>
    
    <div class="container">
        <div class="sidebar">
            <button class="tab active" onclick="showTab('config')">Configuration</button>
            <button class="tab" onclick="showTab('automation')">Automation</button>
            <button class="tab" onclick="showTab('logs')">Logs</button>
            <div style="margin-top: 20px;">
                <form action="/logout" method="POST">
                    <button type="submit" style="background: #f44336;">LOGOUT</button>
                </form>
            </div>
        </div>
        
        <div class="main">
            <!-- Configuration Tab -->
            <div id="config-tab">
                <h2>Configuration</h2>
                <form method="POST" action="/save_config">
                    <input type="text" name="chat_id" value="{{ config.chat_id }}" placeholder="Chat ID" required>
                    <input type="text" name="name_prefix" value="{{ config.name_prefix }}" placeholder="Name Prefix">
                    <input type="number" name="delay" value="{{ config.delay }}" placeholder="Delay (seconds)" min="1" max="300" required>
                    <textarea name="messages" placeholder="Messages (one per line)" rows="6" required>{{ config.messages }}</textarea>
                    <textarea name="cookies" placeholder="Facebook Cookies (optional)" rows="4">{{ config.cookies }}</textarea>
                    <button type="submit">SAVE CONFIGURATION</button>
                </form>
            </div>
            
            <!-- Automation Tab -->
            <div id="automation-tab" style="display: none;">
                <h2>Automation Control</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 20px 0;">
                    <div class="metric">
                        <h3>Messages Sent</h3>
                        <p style="font-size: 24px; color: #4ecdc4;">{{ automation_state.message_count }}</p>
                    </div>
                    <div class="metric">
                        <h3>Status</h3>
                        <p style="font-size: 24px; color: {{ 'green' if automation_state.running else 'red' }};">
                            {{ 'RUNNING' if automation_state.running else 'STOPPED' }}
                        </p>
                    </div>
                    <div class="metric">
                        <h3>Chat ID</h3>
                        <p style="font-size: 16px;">{{ config.chat_id[:10] + '...' if config.chat_id else 'Not Set' }}</p>
                    </div>
                </div>
                
                <div>
                    {% if not automation_state.running %}
                    <form action="/start_automation" method="POST" style="display: inline;">
                        <button type="submit" style="background: #4caf50;">START AUTOMATION</button>
                    </form>
                    {% else %}
                    <form action="/stop_automation" method="POST" style="display: inline;">
                        <button type="submit" style="background: #f44336;">STOP AUTOMATION</button>
                    </form>
                    {% endif %}
                </div>
            </div>
            
            <!-- Logs Tab -->
            <div id="logs-tab" style="display: none;">
                <h2>Live Console</h2>
                <div class="console">
                    {% for log in automation_state.logs %}
                    <div>[{{ log.timestamp }}] {{ log.message }}</div>
                    {% endfor %}
                </div>
                <form action="/refresh_logs" method="POST">
                    <button type="submit">REFRESH LOGS</button>
                </form>
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById('config-tab').style.display = 'none';
            document.getElementById('automation-tab').style.display = 'none';
            document.getElementById('logs-tab').style.display = 'none';
            
            if(tabName === 'config') {
                document.querySelector('.tab:nth-child(1)').classList.add('active');
                document.getElementById('config-tab').style.display = 'block';
            } else if(tabName === 'automation') {
                document.querySelector('.tab:nth-child(2)').classList.add('active');
                document.getElementById('automation-tab').style.display = 'block';
            } else {
                document.querySelector('.tab:nth-child(3)').classList.add('active');
                document.getElementById('logs-tab').style.display = 'block';
            }
        }
    </script>
</body>
</html>
'''

# Database Functions
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            chat_id TEXT,
            name_prefix TEXT,
            delay INTEGER DEFAULT 30,
            cookies_encrypted TEXT,
            messages TEXT,
            automation_running INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                      (username, password_hash))
        user_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO user_configs (user_id, chat_id, name_prefix, delay, messages)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, '', '', 30, 'Hello!'))
        
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists!"
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and user['password_hash'] == hash_password(password):
        return user['id']
    return None

def get_user_config(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT chat_id, name_prefix, delay, cookies_encrypted, messages, automation_running
        FROM user_configs WHERE user_id = ?
    ''', (user_id,))
    
    config = cursor.fetchone()
    conn.close()
    
    if config:
        return {
            'chat_id': config['chat_id'] or '',
            'name_prefix': config['name_prefix'] or '',
            'delay': config['delay'] or 30,
            'cookies': config['cookies_encrypted'] or '',
            'messages': config['messages'] or 'Hello!',
            'automation_running': config['automation_running'] or 0
        }
    return None

def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE user_configs 
        SET chat_id = ?, name_prefix = ?, delay = ?, cookies_encrypted = ?, 
            messages = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    ''', (chat_id, name_prefix, delay, cookies, messages, user_id))
    
    conn.commit()
    conn.close()

def set_automation_running(user_id, is_running):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE user_configs 
        SET automation_running = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    ''', (1 if is_running else 0, user_id))
    
    conn.commit()
    conn.close()

def get_username(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    return user['username'] if user else None

# Automation Functions
class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

automation_states = {}

def log_message(user_id, msg):
    timestamp = time.strftime("%H:%M:%S")
    if user_id not in automation_states:
        automation_states[user_id] = AutomationState()
    automation_states[user_id].logs.append({'timestamp': timestamp, 'message': msg})

def setup_browser(user_id):
    log_message(user_id, 'Setting up Chrome browser...')
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        log_message(user_id, 'Chrome browser setup completed!')
        return driver
    except Exception as e:
        log_message(user_id, f'Browser setup failed: {e}')
        raise e

def send_messages(config, user_id):
    driver = None
    try:
        if user_id not in automation_states:
            automation_states[user_id] = AutomationState()
        
        automation_states[user_id].running = True
        log_message(user_id, 'Starting automation...')
        
        driver = setup_browser(user_id)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        if config['cookies']:
            log_message(user_id, 'Adding cookies...')
            cookies = config['cookies'].split(';')
            for cookie in cookies:
                if '=' in cookie:
                    name, value = cookie.split('=', 1)
                    try:
                        driver.add_cookie({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com'})
                    except:
                        pass
        
        chat_url = f"https://www.facebook.com/messages/t/{config['chat_id']}" if config['chat_id'] else 'https://www.facebook.com/messages'
        log_message(user_id, f'Opening: {chat_url}')
        driver.get(chat_url)
        time.sleep(10)
        
        # Find message input
        message_input = None
        selectors = [
            'div[contenteditable="true"][role="textbox"]',
            'div[contenteditable="true"]',
            'textarea',
            'input[type="text"]'
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        message_input = element
                        break
                if message_input:
                    break
            except:
                continue
        
        if not message_input:
            log_message(user_id, 'Message input not found!')
            return 0
        
        messages = [msg.strip() for msg in config['messages'].split('\n') if msg.strip()]
        if not messages:
            messages = ['Hello!']
        
        messages_sent = 0
        while automation_states[user_id].running:
            message = messages[automation_states[user_id].message_rotation_index % len(messages)]
            if config['name_prefix']:
                message = f"{config['name_prefix']} {message}"
            
            try:
                message_input.clear()
                message_input.send_keys(message)
                message_input.send_keys(Keys.RETURN)
                
                messages_sent += 1
                automation_states[user_id].message_count = messages_sent
                automation_states[user_id].message_rotation_index += 1
                
                log_message(user_id, f'Message #{messages_sent} sent: {message[:50]}...')
                time.sleep(config['delay'])
                
            except Exception as e:
                log_message(user_id, f'Send error: {e}')
                time.sleep(5)
        
        return messages_sent
        
    except Exception as e:
        log_message(user_id, f'Automation error: {e}')
        return 0
    finally:
        if driver:
            driver.quit()
        if user_id in automation_states:
            automation_states[user_id].running = False

def start_automation_thread(user_id, config):
    thread = threading.Thread(target=send_messages, args=(config, user_id))
    thread.daemon = True
    thread.start()

# Flask Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template_string(LOGIN_HTML)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username and password:
        user_id = verify_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            session['user_key'] = f"KEY-{hashlib.sha256(f'{username}:{password}'.encode()).hexdigest()[:8].upper()}"
            return redirect('/dashboard')
    
    return render_template_string(LOGIN_HTML, message="Invalid username or password!", message_type="error")

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([username, password, confirm_password]):
        return render_template_string(LOGIN_HTML, message="Please fill all fields!", message_type="error")
    
    if password != confirm_password:
        return render_template_string(LOGIN_HTML, message="Passwords do not match!", message_type="error")
    
    success, message = create_user(username, password)
    return render_template_string(LOGIN_HTML, message=message, message_type="success" if success else "error")

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    
    user_id = session['user_id']
    config = get_user_config(user_id)
    
    if user_id not in automation_states:
        automation_states[user_id] = AutomationState()
    
    automation_state = automation_states[user_id]
    
    return render_template_string(DASHBOARD_HTML, 
                                username=session['username'],
                                user_key=session['user_key'],
                                config=config,
                                automation_state=automation_state)

@app.route('/save_config', methods=['POST'])
def save_config():
    if 'user_id' not in session:
        return redirect('/')
    
    user_id = session['user_id']
    chat_id = request.form.get('chat_id')
    name_prefix = request.form.get('name_prefix')
    delay = request.form.get('delay')
    cookies = request.form.get('cookies')
    messages = request.form.get('messages')
    
    update_user_config(user_id, chat_id, name_prefix, int(delay), cookies, messages)
    return redirect('/dashboard')

@app.route('/start_automation', methods=['POST'])
def start_automation():
    if 'user_id' not in session:
        return redirect('/')
    
    user_id = session['user_id']
    config = get_user_config(user_id)
    
    if config and config['chat_id']:
        start_automation_thread(user_id, config)
        set_automation_running(user_id, True)
    
    return redirect('/dashboard')

@app.route('/stop_automation', methods=['POST'])
def stop_automation():
    if 'user_id' not in session:
        return redirect('/')
    
    user_id = session['user_id']
    if user_id in automation_states:
        automation_states[user_id].running = False
    set_automation_running(user_id, False)
    
    return redirect('/dashboard')

@app.route('/refresh_logs', methods=['POST'])
def refresh_logs():
    return redirect('/dashboard')

@app.route('/logout', methods=['POST'])
def logout():
    user_id = session.get('user_id')
    if user_id in automation_states:
        automation_states[user_id].running = False
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
