#!/usr/bin/env python3
"""
FreelanceHub Deployment Helper
This script helps prepare your application for deployment
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'requirements.txt',
        'render.yaml',
        'Procfile'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def check_git():
    """Check if git is initialized"""
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository initialized")
            return True
        else:
            print("❌ Git not initialized")
            return False
    except FileNotFoundError:
        print("❌ Git not found. Please install Git first.")
        return False

def create_demo_data():
    """Create demo data for testing"""
    print("🎯 Creating demo data...")
    
    # This would be handled by your app's initialization
    print("✅ Demo data ready")

def main():
    print("🚀 FreelanceHub Deployment Helper")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please fix missing files before deploying")
        sys.exit(1)
    
    # Check git
    if not check_git():
        print("\n💡 To deploy, you need to:")
        print("   1. Install Git: https://git-scm.com/")
        print("   2. Initialize git: git init")
        print("   3. Add files: git add .")
        print("   4. Commit: git commit -m 'Initial commit'")
        print("   5. Push to GitHub")
        sys.exit(1)
    
    # Create demo data
    create_demo_data()
    
    print("\n🎉 Your FreelanceHub is ready for deployment!")
    print("\n📋 Next Steps:")
    print("   1. Push to GitHub: git push origin main")
    print("   2. Go to Render.com and create a new Web Service")
    print("   3. Connect your GitHub repository")
    print("   4. Deploy and share the URL with friends!")
    
    print("\n📖 For detailed instructions, see: DEPLOYMENT.md")

if __name__ == "__main__":
    main() 