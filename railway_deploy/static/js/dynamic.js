/**
 * FreelanceHub Dynamic Features JavaScript
 * This file contains all the JavaScript code for the dynamic features of FreelanceHub
 */

// Initialize socket connection for real-time features
let socket;

// Get current user ID from the DOM if available
let currentUserId = null;

document.addEventListener('DOMContentLoaded', function() {
    // Get current user ID if user is logged in
    const userData = document.getElementById('user-data');
    if (userData) {
        currentUserId = userData.dataset.userId;
        console.log('Current user ID:', currentUserId);
    }
    
    // Initialize Socket.IO connection
    initializeSocket();
    
    // Initialize dynamic search if search box exists
    initializeDynamicSearch();
    
    // Initialize notifications
    initializeNotifications();
    
    // Initialize chat if on order page
    if (document.querySelector('#chat-container')) {
        initializeChat();
    }
    
    // Initialize trending services on homepage
    if (document.querySelector('#trending-services')) {
        loadTrendingServices();
    }
    
    // Initialize user stats on profile page
    if (document.querySelector('#user-stats')) {
        loadUserStats();
    }
});

/**
 * Initialize Socket.IO connection
 */
function initializeSocket() {
    try {
        socket = io();
        
        socket.on('connect', function() {
            console.log('Socket connected successfully');
            socket.emit('join_room', {});
        });
        
        socket.on('room_joined', function(data) {
            console.log('Joined room:', data.room);
        });
        
        socket.on('notification', function(data) {
            showNotification(data.message, data.type);
        });
        
        socket.on('new_message', function(data) {
            appendChatMessage(data);
        });
        
        socket.on('connect_error', function(error) {
            console.error('Socket connection error:', error);
        });
    } catch (error) {
        console.error('Error initializing socket:', error);
    }
}

/**
 * Initialize dynamic search functionality
 */
function initializeDynamicSearch() {
    const searchBox = document.querySelector('.search-box');
    if (!searchBox) return;
    
    const resultsContainer = document.createElement('div');
    resultsContainer.className = 'search-results';
    resultsContainer.style.display = 'none';
    searchBox.parentNode.appendChild(resultsContainer);
    
    let debounceTimer;
    
    searchBox.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(debounceTimer);
        
        if (query.length < 2) {
            resultsContainer.style.display = 'none';
            return;
        }
        
        debounceTimer = setTimeout(function() {
            fetch(`/api/search_services?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    resultsContainer.innerHTML = '';
                    
                    if (data.length === 0) {
                        resultsContainer.innerHTML = '<div class="no-results">No services found</div>';
                    } else {
                        data.forEach(service => {
                            const resultItem = document.createElement('div');
                            resultItem.className = 'result-item';
                            resultItem.innerHTML = `
                                <a href="/service/${service.id}">
                                    <div class="result-title">${service.title}</div>
                                    <div class="result-meta">
                                        <span class="result-price">$${service.price}</span>
                                        <span class="result-freelancer">by ${service.freelancer}</span>
                                    </div>
                                </a>
                            `;
                            resultsContainer.appendChild(resultItem);
                        });
                    }
                    
                    resultsContainer.style.display = 'block';
                })
                .catch(error => {
                    console.error('Error searching services:', error);
                });
        }, 300);
    });
    
    // Hide search results when clicking outside
    document.addEventListener('click', function(event) {
        if (!searchBox.contains(event.target) && !resultsContainer.contains(event.target)) {
            resultsContainer.style.display = 'none';
        }
    });
}

/**
 * Initialize notifications system
 */
function initializeNotifications() {
    // Create notifications container if it doesn't exist
    let notificationsContainer = document.querySelector('#notifications-container');
    
    if (!notificationsContainer) {
        notificationsContainer = document.createElement('div');
        notificationsContainer.id = 'notifications-container';
        document.body.appendChild(notificationsContainer);
    }
    
    // Load initial notifications
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            data.forEach(notification => {
                showNotification(notification.message, notification.type);
            });
        })
        .catch(error => {
            console.error('Error loading notifications:', error);
        });
}

/**
 * Show a notification message
 */
function showNotification(message, type = 'info') {
    const notificationsContainer = document.querySelector('#notifications-container');
    
    if (!notificationsContainer) return;
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    notificationsContainer.appendChild(notification);
    
    // Add close button functionality
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', function() {
        notification.classList.add('notification-hiding');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.classList.add('notification-hiding');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

/**
 * Initialize chat functionality
 */
function initializeChat() {
    const chatContainer = document.querySelector('#chat-container');
    const messageInput = document.querySelector('#message-input');
    const sendButton = document.querySelector('#send-message');
    const orderId = chatContainer.dataset.orderId;
    
    if (!chatContainer || !messageInput || !sendButton || !orderId) return;
    
    // Load existing messages
    loadChatMessages(orderId);
    
    // Join order room
    socket.emit('join_room', { room: `order_${orderId}` });
    
    // Send message handler
    sendButton.addEventListener('click', function() {
        sendChatMessage(orderId, messageInput.value);
    });
    
    // Send on Enter key
    messageInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendChatMessage(orderId, messageInput.value);
        }
    });
}

/**
 * Load chat messages for an order
 */
function loadChatMessages(orderId) {
    fetch(`/api/chat/${orderId}`)
        .then(response => response.json())
        .then(data => {
            const messagesContainer = document.querySelector('#chat-messages');
            
            if (!messagesContainer) return;
            
            messagesContainer.innerHTML = '';
            
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    appendChatMessage(message);
                });
            } else {
                messagesContainer.innerHTML = '<div class="chat-notice">No messages yet. Start the conversation!</div>';
            }
        })
        .catch(error => {
            console.error('Error loading chat messages:', error);
        });
}

/**
 * Send a chat message
 */
function sendChatMessage(orderId, message) {
    if (!message.trim()) return;
    
    const messageInput = document.querySelector('#message-input');
    
    socket.emit('send_message', {
        order_id: orderId,
        message: message.trim()
    });
    
    // Clear input field
    messageInput.value = '';
}

/**
 * Append a chat message to the chat container
 */
function appendChatMessage(message) {
    const messagesContainer = document.querySelector('#chat-messages');
    
    if (!messagesContainer) return;
    
    // Remove the "no messages" notice if it exists
    const noMessagesNotice = messagesContainer.querySelector('.chat-notice');
    if (noMessagesNotice) {
        noMessagesNotice.remove();
    }
    
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${message.user_id === currentUserId ? 'chat-message-own' : 'chat-message-other'}`;
    
    const timestamp = new Date(message.timestamp);
    const formattedTime = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageElement.innerHTML = `
        <div class="chat-message-header">
            <span class="chat-message-sender">${message.username}</span>
            <span class="chat-message-time">${formattedTime}</span>
        </div>
        <div class="chat-message-content">${message.message}</div>
    `;
    
    messagesContainer.appendChild(messageElement);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Load trending services for homepage
 */
function loadTrendingServices() {
    const trendingContainer = document.querySelector('#trending-services');
    
    if (!trendingContainer) return;
    
    fetch('/api/trending_services')
        .then(response => response.json())
        .then(data => {
            trendingContainer.innerHTML = '';
            
            if (data.length === 0) {
                trendingContainer.innerHTML = '<div class="no-trending">No trending services yet</div>';
                return;
            }
            
            data.forEach(service => {
                const serviceCard = document.createElement('div');
                serviceCard.className = 'col-md-4 mb-4';
                serviceCard.innerHTML = `
                    <div class="card service-card">
                        <div class="card-body">
                            <h5 class="card-title">${service.title}</h5>
                            <p class="card-text">
                                <span class="service-price">$${service.price}</span>
                                <span class="service-freelancer">by ${service.freelancer}</span>
                            </p>
                            <div class="trending-badge">
                                <i class="fas fa-fire"></i> Trending
                                <span class="order-count">${service.order_count} orders</span>
                            </div>
                            <a href="/service/${service.id}" class="btn btn-primary mt-2">View Details</a>
                        </div>
                    </div>
                `;
                trendingContainer.appendChild(serviceCard);
            });
        })
        .catch(error => {
            console.error('Error loading trending services:', error);
        });
}

/**
 * Load user statistics for profile page
 */
function loadUserStats() {
    const statsContainer = document.querySelector('#user-stats');
    
    if (!statsContainer) return;
    
    const userId = statsContainer.dataset.userId;
    
    if (!userId) return;
    
    fetch(`/api/user_stats/${userId}`)
        .then(response => response.json())
        .then(data => {
            // Update stats in the UI
            Object.keys(data).forEach(key => {
                const statElement = document.querySelector(`#stat-${key}`);
                if (statElement) {
                    if (key.includes('rate') || key.includes('percentage')) {
                        statElement.textContent = `${Math.round(data[key])}%`;
                    } else if (key.includes('earnings') || key.includes('spent')) {
                        statElement.textContent = `$${data[key].toFixed(2)}`;
                    } else {
                        statElement.textContent = data[key];
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading user stats:', error);
        });
}