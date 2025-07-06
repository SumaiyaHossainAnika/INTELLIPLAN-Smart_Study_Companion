#!/usr/bin/env python3
"""
🌐 Cross-Network Setup Helper for Intelliplan
Helps set up internet access for different WiFi networks
"""

import os
import sys
import subprocess
import socket
import requests
import json
from pathlib import Path

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to Google DNS to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def check_ngrok_installed():
    """Check if ngrok is installed and available"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def download_ngrok():
    """Download ngrok if not available"""
    print("📥 ngrok not found. Let me help you set it up!")
    print("\n🔗 Please follow these steps:")
    print("1. Go to https://ngrok.com/download")
    print("2. Sign up for a free account")
    print("3. Download ngrok for Windows")
    print("4. Extract ngrok.exe to this folder:")
    print(f"   {os.path.dirname(os.path.abspath(__file__))}")
    print("5. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken")
    print("\n📋 After downloading, run this script again!")
    return False

def setup_ngrok_auth():
    """Setup ngrok authentication"""
    print("\n🔑 Setting up ngrok authentication...")
    print("📝 You need your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken")
    
    authtoken = input("\n🔐 Enter your ngrok authtoken: ").strip()
    if not authtoken:
        print("❌ No authtoken provided!")
        return False
    
    try:
        result = subprocess.run(['ngrok', 'authtoken', authtoken], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok authentication successful!")
            return True
        else:
            print(f"❌ Authentication failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error setting up auth: {e}")
        return False

def test_server_running():
    """Test if the Flask server is running"""
    try:
        response = requests.get("http://localhost:5000", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_ngrok_tunnel():
    """Start ngrok tunnel"""
    print("\n🚀 Starting ngrok tunnel...")
    print("🔄 This will create a public URL for your Intelliplan app...")
    
    try:
        # Start ngrok in background
        process = subprocess.Popen(['ngrok', 'http', '5000'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait a moment for ngrok to start
        import time
        time.sleep(3)
        
        # Get the public URL
        try:
            response = requests.get("http://localhost:4040/api/tunnels")
            data = response.json()
            
            if data['tunnels']:
                public_url = data['tunnels'][0]['public_url']
                print(f"\n🎉 SUCCESS! Your Intelliplan app is now accessible at:")
                print(f"🔗 {public_url}")
                print(f"\n📱 Share this URL via WhatsApp:")
                print(f"   Hey! Join my study group: {public_url}")
                print(f"\n⚠️  Important notes:")
                print(f"   • Keep this terminal open to maintain the connection")
                print(f"   • Free ngrok sessions last 2 hours")
                print(f"   • URL changes each time you restart ngrok")
                return public_url
            else:
                print("❌ Could not get ngrok URL")
                return None
                
        except Exception as e:
            print(f"❌ Error getting ngrok URL: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return None

def create_whatsapp_message(url):
    """Create a WhatsApp-ready message"""
    message = f"""🎓 Join my Intelliplan study group!

📚 Access the app here: {url}

📋 Steps to join:
1. Click the link above
2. Create an account or login
3. I'll share the group code with you
4. Join our study group and let's collaborate!

💡 This works on any device with internet access"""
    
    return message

def main():
    """Main setup function"""
    print("🌐 Intelliplan Cross-Network Setup Helper")
    print("=" * 50)
    
    # Get local IP
    local_ip = get_local_ip()
    print(f"🏠 Your local IP: {local_ip}")
    
    # Check if server is running
    if test_server_running():
        print("✅ Flask server is running on localhost:5000")
    else:
        print("❌ Flask server not detected!")
        print("📝 Please start your server first: python intelliplan.py")
        print("   Then run this script again.")
        return
    
    print("\n📡 Choose your cross-network option:")
    print("1. 🌍 ngrok (Internet access - Recommended)")
    print("2. 🏠 Local network only (same WiFi)")
    print("3. 📖 View all options")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        # ngrok setup
        if not check_ngrok_installed():
            if not download_ngrok():
                return
        
        # Setup auth if needed
        setup_ngrok_auth()
        
        # Start tunnel
        public_url = start_ngrok_tunnel()
        if public_url:
            # Create WhatsApp message
            whatsapp_msg = create_whatsapp_message(public_url)
            print(f"\n📱 WhatsApp message ready:")
            print("-" * 40)
            print(whatsapp_msg)
            print("-" * 40)
            
            print(f"\n🔄 Keep this terminal open to maintain the connection!")
            print(f"🛑 Press Ctrl+C to stop the tunnel")
            
            try:
                input("\nPress Enter to stop the tunnel...")
            except KeyboardInterrupt:
                print(f"\n🛑 Stopping ngrok tunnel...")
    
    elif choice == "2":
        # Local network
        print(f"\n🏠 Local Network Access:")
        print(f"📍 Share this URL with friends on your WiFi:")
        print(f"🔗 http://{local_ip}:5000")
        print(f"\n📱 WhatsApp message:")
        print(f"   🎓 Join my study group: http://{local_ip}:5000")
        print(f"   📶 Make sure you're on my WiFi network!")
    
    elif choice == "3":
        # Show all options
        print(f"\n📖 All Cross-Network Options:")
        print(f"\n1. 🌍 ngrok (Internet Access):")
        print(f"   • Works across different WiFi networks")
        print(f"   • Perfect for WhatsApp sharing")
        print(f"   • Free tier: 2-hour sessions")
        print(f"\n2. 🏠 Port Forwarding:")
        print(f"   • Permanent internet access")
        print(f"   • Requires router configuration")
        print(f"   • Security considerations needed")
        print(f"\n3. 🔒 VPN Network:")
        print(f"   • Secure virtual network")
        print(f"   • All users need VPN app")
        print(f"   • Works like same WiFi")
        print(f"\n4. 📶 Same WiFi Only:")
        print(f"   • URL: http://{local_ip}:5000")
        print(f"   • All users on same network")
        print(f"   • No additional setup needed")
    
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
