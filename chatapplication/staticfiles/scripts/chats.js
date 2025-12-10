
    // Get DOM elements
    const messageInput = document.querySelector('.message-input');
    const sendBtn = document.querySelector('.send-btn');
    const messagesContainer = document.querySelector('.messages-container');
    const chatItems = document.querySelectorAll('.chat-item');

    // Fallback save URL; template will set window.SAVE_MESSAGE_URL when available
    const SAVE_MESSAGE_URL = window.SAVE_MESSAGE_URL || '/users/api/save-message/';

    // Helper to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Add message element to UI
    function addMessageToUI(content, timeStr) {
        if (!messagesContainer) return;
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message own';
        messageDiv.innerHTML = `
            <div>
                <div class="message-content">${escapeHtml(content)}</div>
                <div class="message-time">${timeStr || new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Helper to escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // WebSocket connection (optional)
    window.socket = null;

    function connectWebSocket() {
        const uid = window.userId || null;
        if (!uid || !window.WS_URL_TEMPLATE) return;
        try {
            const wsUrl = window.WS_URL_TEMPLATE.replace('/0/', `/${uid}/`);
            window.socket = new WebSocket(wsUrl);

            window.socket.onopen = function() {
                console.log('WebSocket connected', wsUrl);
            };

            window.socket.onmessage = function(event) {
                try {
                    const msg = JSON.parse(event.data);
                    if (msg && msg.content) {
                        addMessageToUI(msg.content, msg.timestamp ? formatTimestamp(msg.timestamp) : null);
                    }
                } catch (e) {
                    console.error('Invalid WS message', e);
                }
            };

            window.socket.onclose = function() {
                console.log('WebSocket closed');
                window.socket = null;
            };
        } catch (e) {
            console.error('WebSocket connection failed', e);
            window.socket = null;
        }
    }

    // Send message function: prefer WebSocket when available, fallback to HTTP
   function sendMessage() {
    const messageInput = document.getElementById("message-input");
    const message = messageInput.value.trim();

    if (message === "" || !window.userId) return;

    // Disable input to prevent duplicate sends
    messageInput.disabled = true;

    // SEND TO BACKEND (SAVES IN DATABASE)
    fetch(window.SAVE_MESSAGE_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: new URLSearchParams({
            user_id: window.userId,
            content: message
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "saved") {
            // Add message to UI with server time
            addMessageToUI(message, data.time);
            messageInput.value = "";
        } else {
            console.error("Failed to save message:", data);
        }
    })
    .catch(err => {
        console.error("Save error:", err);
    })
    .finally(() => {
        messageInput.disabled = false;
        messageInput.focus();
    });
    scrollChat();

}


    // Helper to format server timestamp 'YYYY-MM-DD HH:MM:SS' to 'h:mm A'
    function formatTimestamp(ts) {
    try {
        // Normalize: replace first space with T, add Z if missing timezone
        let iso = ts.trim().replace(' ', 'T');
        if (!/[zZ]$/.test(iso) && !/[+-]\d{2}:?\d{2}$/.test(iso)) {
            iso += 'Z'; // assume UTC if no timezone
        }

        const d = new Date(iso);
        if (isNaN(d.getTime())) return ts;

        return d.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return ts;
    }
}

    // Event listeners
    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = Math.min(messageInput.scrollHeight, 100) + 'px';
        });
    }

    // Chat item click handler (visual only)
    chatItems.forEach(item => {
        item.addEventListener('click', () => {
            chatItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });

    // Load messages for current user on page load
    function loadMessages() {
        const uid = window.userId || null;
        if (!uid) return;

        // Build messages URL from template: replace trailing '0' with uid
        let urlTemplate = window.MESSAGES_URL_TEMPLATE || '/users/api/messages/0/';
        const url = urlTemplate.replace('/0/', `/${uid}/`);

        fetch(url, { method: 'GET' })
            .then(res => res.json())
            .then(data => {
                // Clear existing messages
                if (messagesContainer) messagesContainer.innerHTML = '';

                if (!Array.isArray(data) || data.length === 0) {
                    if (messagesContainer) {
                        messagesContainer.innerHTML = `\n                        <div class="message">\n                            <div>\n                                <div class="message-content">No messages yet. Start a conversation!</div>\n                                <div class="message-time">--</div>\n                            </div>\n                        </div>`;
                    }
                    return;
                }

                data.forEach(m => {
                    const content = m.content || '';
                    const ts = m.timestamp || null;
                    addMessageToUI(content, ts ? formatTimestamp(ts) : null);
                });
            })
            .catch(err => console.error('Error loading messages:', err));
    }

    document.addEventListener('DOMContentLoaded', function() {
        loadMessages();
        connectWebSocket();
    });

    function scrollChat() {
    const box = document.querySelector('.messages-container');
    if (box) box.scrollTop = box.scrollHeight;
}


