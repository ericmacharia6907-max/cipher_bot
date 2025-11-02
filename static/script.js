let isTyping = false;
let currentMood = 'neutral';

// DOM Elements
const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const typingIndicator = document.getElementById('typingIndicator');
const robotFace = document.getElementById('robotFace');
const userInfo = document.getElementById('userInfo');
const userName = document.getElementById('userName');

// Robot faces
const faces = {
    neutral: '◕‿◕',
    happy: '^_^',
    thinking: '⊙_⊙',
    excited: '✧◕‿◕✧'
};

// Initialize
async function init() {
    try {
        const response = await fetch('/init');
        const data = await response.json();
        
        if (data.user_data.name) {
            userName.textContent = data.user_data.name;
            userInfo.style.display = 'block';
        }
        
        addMessage(data.greeting, 'cipher');
    } catch (error) {
        console.error('Init error:', error);
        addMessage("Oops! Something went wrong with my circuits. Try refreshing?", 'cipher');
    }
}

// Add message to chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.textContent = text;
    
    messageDiv.appendChild(bubbleDiv);
    messagesContainer.appendChild(messageDiv);
    
    scrollToBottom();
}

// Scroll to bottom
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Change robot face
function changeFace(mood) {
    currentMood = mood;
    robotFace.textContent = faces[mood] || faces.neutral;
}

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (message === '' || isTyping) return;
    
    // Add user message
    addMessage(message, 'user');
    messageInput.value = '';
    
    // Show typing indicator
    isTyping = true;
    sendButton.disabled = true;
    typingIndicator.style.display = 'flex';
    changeFace('thinking');
    scrollToBottom();
    
    try {
        // Simulate typing delay
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
        
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        typingIndicator.style.display = 'none';
        
        // Add bot response
        addMessage(data.response, 'cipher');
        
        // Update user info if name is set
        if (data.user_data.name && !userName.textContent) {
            userName.textContent = data.user_data.name;
            userInfo.style.display = 'block';
        }
        
        // Change to happy face briefly
        changeFace('happy');
        setTimeout(() => changeFace('neutral'), 2000);
        
    } catch (error) {
        console.error('Send error:', error);
        typingIndicator.style.display = 'none';
        addMessage("Uh oh, my circuits are acting up! Can you try that again?", 'cipher');
    }
    
    isTyping = false;
    sendButton.disabled = false;
    messageInput.focus();
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Initialize on load
init();