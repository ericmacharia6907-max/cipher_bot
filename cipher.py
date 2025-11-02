from flask import Flask, render_template, request, jsonify, session
import json
import os
from bot_logic import CipherBot

app = Flask(__name__)
app.secret_key = 'cipher-secret-key-change-this-in-production'  # Change this!

# ADD YOUR HUGGING FACE API KEY HERE
HUGGING_FACE_API_KEY = "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"# Replace with your actual key from huggingface.co

# Store user data in a simple JSON file
DATA_FILE = 'user_data.json'

def load_user_data():
    """Load user data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_user_data(data):
    """Save user data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving user data: {e}")

@app.route('/')
def index():
    """Render the main chat page"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        user_message = request.json.get('message', '')
        
        if not user_message.strip():
            return jsonify({'error': 'Empty message'}), 400
        
        # Get or create user session
        if 'user_id' not in session:
            session['user_id'] = os.urandom(16).hex()
        
        user_id = session['user_id']
        
        # Load all user data
        all_data = load_user_data()
        user_data = all_data.get(user_id, {
            'name': '',
            'interests': [],
            'facts': [],
            'topics': []
        })
        
        # Get bot response with AI
        bot = CipherBot(user_data, HUGGING_FACE_API_KEY)
        response, updated_data = bot.get_response(user_message)
        
        # Save updated data
        all_data[user_id] = updated_data
        save_user_data(all_data)
        
        return jsonify({
            'response': response,
            'user_data': updated_data
        })
    
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            'response': "Oops! My circuits got tangled. Can you try that again? 🤖",
            'user_data': user_data if 'user_data' in locals() else {}
        })

@app.route('/init', methods=['GET'])
def init():
    """Initialize chat session and get greeting"""
    try:
        if 'user_id' not in session:
            session['user_id'] = os.urandom(16).hex()
        
        user_id = session['user_id']
        all_data = load_user_data()
        user_data = all_data.get(user_id, {
            'name': '',
            'interests': [],
            'facts': [],
            'topics': []
        })
        
        # Get greeting with AI
        bot = CipherBot(user_data, HUGGING_FACE_API_KEY)
        greeting = bot.get_greeting()
        
        return jsonify({
            'greeting': greeting,
            'user_data': user_data
        })
    
    except Exception as e:
        print(f"Init error: {e}")
        return jsonify({
            'greeting': "Well, well, well... A new human! I'm Cipher, your friendly neighborhood sarcastic robot. What should I call you?",
            'user_data': {
                'name': '',
                'interests': [],
                'facts': [],
                'topics': []
            }
        })

@app.route('/reset', methods=['POST'])
def reset():
    """Reset user data (optional endpoint for testing)"""
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            all_data = load_user_data()
            if user_id in all_data:
                del all_data[user_id]
                save_user_data(all_data)
        
        session.clear()
        return jsonify({'success': True, 'message': 'Data reset successfully'})
    
    except Exception as e:
        print(f"Reset error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    print(f"Server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create data file if it doesn't exist
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
    
    print("🤖 Cipher is booting up...")
    print("📡 Server running at: http://127.0.0.1:5000")
    print("💡 Press CTRL+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)