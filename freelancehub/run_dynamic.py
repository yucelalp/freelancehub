#!/usr/bin/env python3
"""
Dynamic FreelanceHub Runner
This script runs the enhanced version of FreelanceHub with real-time features.
"""

import os
import sys
from app import app, socketio, db

def main():
    """Main function to run the dynamic FreelanceHub application"""
    
    print("🚀 Starting Dynamic FreelanceHub...")
    print("=" * 50)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database initialized")
    
    # Check if static/js directory exists
    js_dir = os.path.join('static', 'js')
    if not os.path.exists(js_dir):
        os.makedirs(js_dir)
        print("✅ Created static/js directory")
    
    print("\n🌐 Starting server...")
    print("📱 Real-time features enabled:")
    print("   • Live notifications")
    print("   • Real-time chat")
    print("   • Dynamic trending services")
    print("   • Live search")
    print("   • User statistics")
    
    print("\n🔗 Access your application at:")
    print("   • Main site: http://localhost:5000")
    print("   • API endpoints: http://localhost:5000/api/")
    
    print("\n⚡ Features now available:")
    print("   • Real-time notifications when orders are placed")
    print("   • Live chat between clients and freelancers")
    print("   • Dynamic trending services based on recent orders")
    print("   • Live search with instant results")
    print("   • Real-time user statistics")
    
    print("\n" + "=" * 50)
    print("🎯 Your FreelanceHub is now LIVE with dynamic features!")
    print("=" * 50)
    
    # Run the application with SocketIO
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main() 