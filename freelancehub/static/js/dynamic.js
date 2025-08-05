// Dynamic features for FreelanceHub
class FreelanceHubDynamic {
    constructor() {
        this.socket = null;
        this.notifications = [];
        this.init();
    }

    init() {
        this.initSocketIO();
        this.initNotifications();
        this.initLiveSearch();
        this.initTrendingServices();
        this.initUserStats();
    }

    initSocketIO() {
        // Initialize Socket.IO connection
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.socket.emit('join_room', { user_id: this.getCurrentUserId() });
        });

        this.socket.on('notification', (data) => {
            this.showNotification(data.message, data.type);
        });

        this.socket.on('new_message', (data) => {
            this.handleNewMessage(data);
        });
    }

    initNotifications() {
        // Check for notifications every 30 seconds
        setInterval(() => {
            this.fetchNotifications();
        }, 30000);

        // Initial fetch
        this.fetchNotifications();
    }

    async fetchNotifications() {
        try {
            const response = await fetch('/api/notifications');
            if (response.ok) {
                const notifications = await response.json();
                this.updateNotificationBadge(notifications.length);
                
                notifications.forEach(notification => {
                    this.showNotification(notification.message, notification.type);
                });
            }
        } catch (error) {
            console.error('Error fetching notifications:', error);
        }
    }

    updateNotificationBadge(count) {
        const badge = document.getElementById('notification-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'order' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        notification.innerHTML = `
            <strong>${type === 'order' ? 'New Order!' : 'Notification'}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    initLiveSearch() {
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            let searchTimeout;
            
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value;
                
                if (query.length >= 2) {
                    searchTimeout = setTimeout(() => {
                        this.performLiveSearch(query);
                    }, 300);
                }
            });
        }
    }

    async performLiveSearch(query) {
        try {
            const response = await fetch(`/api/search_services?q=${encodeURIComponent(query)}`);
            if (response.ok) {
                const results = await response.json();
                this.displaySearchResults(results);
            }
        } catch (error) {
            console.error('Error performing live search:', error);
        }
    }

    displaySearchResults(results) {
        let searchResultsContainer = document.getElementById('live-search-results');
        
        if (!searchResultsContainer) {
            searchResultsContainer = document.createElement('div');
            searchResultsContainer.id = 'live-search-results';
            searchResultsContainer.className = 'position-absolute bg-white border rounded shadow-sm';
            searchResultsContainer.style.cssText = 'top: 100%; left: 0; right: 0; z-index: 1000; max-height: 300px; overflow-y: auto;';
            
            const searchContainer = document.querySelector('.search-box').parentElement;
            searchContainer.style.position = 'relative';
            searchContainer.appendChild(searchResultsContainer);
        }
        
        if (results.length === 0) {
            searchResultsContainer.innerHTML = '<div class="p-3 text-muted">No services found</div>';
            return;
        }
        
        searchResultsContainer.innerHTML = results.map(service => `
            <a href="/service/${service.id}" class="d-block p-3 text-decoration-none border-bottom">
                <div class="fw-bold">${service.title}</div>
                <div class="text-muted small">by ${service.freelancer} • $${service.price}</div>
            </a>
        `).join('');
    }

    async initTrendingServices() {
        try {
            const response = await fetch('/api/trending_services');
            if (response.ok) {
                const trendingServices = await response.json();
                this.displayTrendingServices(trendingServices);
            }
        } catch (error) {
            console.error('Error fetching trending services:', error);
        }
    }

    displayTrendingServices(services) {
        const container = document.getElementById('trending-services');
        if (container && services.length > 0) {
            container.innerHTML = `
                <div class="row g-4">
                    ${services.map(service => `
                        <div class="col-md-6 col-lg-3">
                            <div class="card h-100">
                                <div class="card-body">
                                    <h6 class="card-title">${service.title}</h6>
                                    <p class="text-muted small">by ${service.freelancer}</p>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <span class="fw-bold text-primary">$${service.price}</span>
                                        <span class="badge bg-success">${service.order_count} orders</span>
                                    </div>
                                    <a href="/service/${service.id}" class="btn btn-sm btn-outline-primary mt-2 w-100">View Service</a>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    }

    async initUserStats() {
        const userId = this.getCurrentUserId();
        if (userId) {
            try {
                const response = await fetch(`/api/user_stats/${userId}`);
                if (response.ok) {
                    const stats = await response.json();
                    this.displayUserStats(stats);
                }
            } catch (error) {
                console.error('Error fetching user stats:', error);
            }
        }
    }

    displayUserStats(stats) {
        const container = document.getElementById('user-stats');
        if (container) {
            if (stats.services_count !== undefined) {
                // Freelancer stats
                container.innerHTML = `
                    <div class="row g-3">
                        <div class="col-6">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="text-primary">${stats.services_count}</h4>
                                    <small class="text-muted">Active Services</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="text-success">$${stats.total_earnings}</h4>
                                    <small class="text-muted">Total Earnings</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="text-info">${stats.completed_orders}</h4>
                                    <small class="text-muted">Completed Orders</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="text-warning">${stats.completion_rate.toFixed(1)}%</h4>
                                    <small class="text-muted">Completion Rate</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                // Client stats
                container.innerHTML = `
                    <div class="row g-3">
                        <div class="col-6">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="text-primary">${stats.orders_placed}</h4>
                                    <small class="text-muted">Orders Placed</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="text-success">$${stats.total_spent}</h4>
                                    <small class="text-muted">Total Spent</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
        }
    }

    handleNewMessage(data) {
        // Handle incoming chat messages
        const chatContainer = document.getElementById('chat-messages');
        if (chatContainer) {
            const messageElement = document.createElement('div');
            messageElement.className = `message ${data.user_id === this.getCurrentUserId() ? 'sent' : 'received'}`;
            messageElement.innerHTML = `
                <div class="message-content">
                    <strong>${data.username}</strong>
                    <p>${data.message}</p>
                    <small class="text-muted">${new Date(data.timestamp).toLocaleTimeString()}</small>
                </div>
            `;
            chatContainer.appendChild(messageElement);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    getCurrentUserId() {
        // Extract user ID from page data or session
        const userDataElement = document.getElementById('user-data');
        if (userDataElement) {
            return userDataElement.dataset.userId;
        }
        return null;
    }
}

// Initialize dynamic features when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FreelanceHubDynamic();
}); 