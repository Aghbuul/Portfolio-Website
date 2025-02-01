document.addEventListener('DOMContentLoaded', function() {
    const chatButton = document.getElementById('chat-button');
    const chatContainer = document.getElementById('chat-container');
    const closeChat = document.getElementById('close-chat');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');

    // Check if all elements exist before adding event listeners
    if (!chatButton || !chatContainer || !closeChat || !chatInput || !sendButton || !chatMessages) {
        console.error('Some chat elements are missing from the DOM');
        return;
    }

    // Toggle chat window
    chatButton.addEventListener('click', () => {
        chatContainer.classList.toggle('hidden');
        if (!chatContainer.classList.contains('hidden')) {
            chatInput.focus();
        }
    });

    closeChat.addEventListener('click', () => {
        chatContainer.classList.add('hidden');
    });

    // Send message function
    async function sendMessage(message) {
        // Add user message to chat
        addMessage(message, 'user');

        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';
        chatMessages.appendChild(typingIndicator);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Remove typing indicator
            typingIndicator.remove();

            if (data.error) {
                throw new Error(data.error);
            }

            // Add bot response to chat
            addMessage(data.response, 'bot');
        } catch (error) {
            console.error('Chat error:', error);
            typingIndicator.remove();
            addMessage('I apologize, but I encountered an error. Please try again in a moment.', 'bot');
        }
    }

    // Add message to chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Handle send button click
    sendButton.addEventListener('click', () => {
        const message = chatInput.value.trim();
        if (message) {
            sendMessage(message);
            chatInput.value = '';
        }
    });

    // Handle enter key
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const message = chatInput.value.trim();
            if (message) {
                sendMessage(message);
                chatInput.value = '';
            }
        }
    });
}); 