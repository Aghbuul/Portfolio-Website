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

    // Global function for handling suggestions
    window.handleSuggestion = function(suggestion) {
        console.log('handleSuggestion called with:', suggestion);

        // Remove the clicked suggestion immediately
        const clickedElement = event.target;
        clickedElement.style.display = 'none';

        // Add user message
        addMessage(suggestion, 'user');

        // Add typing indicator before sending message
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Send message and handle response
        sendMessage(suggestion).then(() => {
            // Remove typing indicator after response
            const indicator = document.querySelector('.typing-indicator');
            if (indicator) {
                indicator.remove();
            }
        });
    };

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

    // Get the base URL for API requests
    const getBaseUrl = () => {
        // Check if we're in the production environment
        if (window.location.hostname.includes('replit.app')) {
            return 'https://' + window.location.hostname;
        }
        // Local development
        return window.location.origin;
    };

    // Send message function
    async function sendMessage(message) {
        console.log('sendMessage called with:', message);
        try {
            const baseUrl = getBaseUrl();
            console.log('Making request to:', `${baseUrl}/chat`);

            const response = await fetch(`${baseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }

            const data = await response.json();
            console.log('Response data:', data);

            // Remove typing indicator before adding response
            const indicator = document.querySelector('.typing-indicator');
            if (indicator) {
                indicator.remove();
            }

            addMessage(data.response, 'bot');
        } catch (error) {
            console.error('Chat error:', error);
            // Remove typing indicator in case of error
            const indicator = document.querySelector('.typing-indicator');
            if (indicator) {
                indicator.remove();
            }
            addMessage('I apologize, but I am temporarily unavailable. Please try again in a moment.', 'bot');
        }
    }

    // Add message to chat
    function addMessage(text, sender) {
        console.log('addMessage called:', { text, sender });
        console.log('Messages before adding:', chatMessages.children.length);

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        if (sender === 'bot') {
            // Convert markdown to HTML
            let formattedText = marked.parse(text);
            console.log('Parsed markdown:', formattedText);

            // Add light cyan color to keywords (text between backticks)
            formattedText = formattedText.replace(
                /`([^`]+)`/g, 
                '<span class="keyword">$1</span>'
            );

            // Make project names clickable (text between asterisks)
            formattedText = formattedText.replace(
                /\*([^*]+)\*/g, 
                '<a href="#" class="project-link" onclick="scrollToProject(\'$1\'); return false;">$1</a>'
            );

            // Make all external links open in new tab
            formattedText = formattedText.replace(
                /<a href="([^"]+)">/g,
                '<a href="$1" target="_blank" rel="noopener noreferrer">'
            );

            messageDiv.innerHTML = formattedText;
        } else {
            messageDiv.textContent = text;
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        console.log('Messages after adding:', chatMessages.children.length);
    }

    // Function to scroll to project card
    function scrollToProject(projectName) {
        const projectCards = document.querySelectorAll('.project-card');
        for (let card of projectCards) {
            if (card.querySelector('h3').textContent.includes(projectName)) {
                card.scrollIntoView({ behavior: 'smooth' });
                card.classList.add('highlight');
                setTimeout(() => card.classList.remove('highlight'), 2000);
                break;
            }
        }
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