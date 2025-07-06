#!/usr/bin/env python3
"""
Cross-Device Setup Helper for Intelliplan
Automatically detects your IP and provides sharing instructions
"""

import socket
import subprocess
import sys

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote server to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except:
        return "127.0.0.1"

def main():
    print("🌐 INTELLIPLAN CROSS-DEVICE SETUP")
    print("=" * 50)
    
    # Get local IP
    local_ip = get_local_ip()
    port = 5000
    
    print(f"📍 Your Computer's IP: {local_ip}")
    print(f"🌐 Network URL: http://{local_ip}:{port}")
    print()
    
    print("📱 WHATSAPP SHARING INSTRUCTIONS:")
    print("-" * 35)
    print("1. Make sure your Intelliplan app is running")
    print("2. Share this URL with friends via WhatsApp:")
    print(f"   👉 http://{local_ip}:{port}")
    print()
    print("3. Requirements:")
    print("   • All users must be on the same WiFi network")
    print("   • Windows Firewall may need to allow port 5000")
    print()
    
    print("🔥 FIREWALL SETUP (if needed):")
    print("-" * 30)
    print("If others can't connect, run this in Administrator Command Prompt:")
    print(f'   netsh advfirewall firewall add rule name="Intelliplan" dir=in action=allow port={port} protocol=TCP')
    print()
    
    print("🚀 INTERNET ACCESS (for different networks):")
    print("-" * 45)
    print("1. Install ngrok: https://ngrok.com/")
    print("2. Run: ngrok http 5000")
    print("3. Share the ngrok URL (e.g., https://abc123.ngrok.io)")
    print()
    
    print("✅ Your app is ready for cross-device chat!")
    print("   Chat messages will sync in real-time across all devices.")

if __name__ == "__main__":
    main()
