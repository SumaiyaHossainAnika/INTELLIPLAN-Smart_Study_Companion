#!/usr/bin/env python3
"""
INTELLIPLAN CROSS-DEVICE SETUP WIZARD
=====================================

This script helps you set up Intelliplan for cross-device access.
It provides multiple options for friends with different IP addresses.
"""

import socket
import subprocess
import platform
import requests
import webbrowser
import time
import os
import sys

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "Unable to determine"

def get_public_ip():
    """Get the public IP address"""
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text.strip()
    except:
        return "Unable to determine"

def check_server_running(ip="localhost", port=5000):
    """Check if the Flask server is running"""
    try:
        response = requests.get(f"http://{ip}:{port}", timeout=3)
        return True
    except:
        return False

def test_firewall():
    """Test if Windows Firewall might be blocking the connection"""
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["netsh", "advfirewall", "firewall", "show", "rule", "name=Intelliplan"],
                capture_output=True, text=True
            )
            return "Intelliplan" in result.stdout
        except:
            return False
    return True

def setup_firewall():
    """Add Windows Firewall rule for Intelliplan"""
    if platform.system() == "Windows":
        try:
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                "name=Intelliplan", "dir=in", "action=allow", 
                "port=5000", "protocol=TCP"
            ], check=True)
            return True
        except:
            return False
    return True

def download_ngrok():
    """Provide instructions for downloading ngrok"""
    print("\n🔽 NGROK SETUP INSTRUCTIONS:")
    print("=" * 50)
    print("1. Go to: https://ngrok.com/")
    print("2. Sign up for a free account")
    print("3. Download ngrok for Windows")
    print("4. Extract ngrok.exe to your Intelliplan folder")
    print("5. Get your auth token from the ngrok dashboard")
    print("6. Run: ngrok authtoken YOUR_AUTH_TOKEN")
    print("7. Start your server: python intelliplan.py")
    print("8. In another terminal: ngrok http 5000")
    print("9. Share the https://xxx.ngrok.io URL with friends")

def main():
    print("=" * 60)
    print("🧠 INTELLIPLAN CROSS-DEVICE SETUP WIZARD")
    print("=" * 60)
    print()
    
    # Get network information
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print("📍 NETWORK INFORMATION:")
    print("-" * 30)
    print(f"Local IP Address: {local_ip}")
    print(f"Public IP Address: {public_ip}")
    print()
    
    # Check if server is running
    server_running = check_server_running()
    print("🖥️  SERVER STATUS:")
    print("-" * 20)
    if server_running:
        print("✅ Intelliplan server is RUNNING")
        print(f"   Local access: http://localhost:5000")
        print(f"   Network access: http://{local_ip}:5000")
    else:
        print("❌ Intelliplan server is NOT running")
        print("   Start it with: python intelliplan.py")
    print()
    
    # Check firewall
    firewall_ok = test_firewall()
    print("🔥 FIREWALL STATUS:")
    print("-" * 20)
    if firewall_ok:
        print("✅ Firewall rule exists or not blocking")
    else:
        print("❌ Firewall may be blocking connections")
        print("   Run as Administrator to fix automatically")
    print()
    
    # Provide setup options
    print("🌐 ACCESS OPTIONS FOR FRIENDS:")
    print("=" * 40)
    print()
    
    print("OPTION 1: Same WiFi Network (Easiest)")
    print("-" * 40)
    print("✅ Best for: Friends in same location")
    print("📋 Steps:")
    print("   1. Make sure friends are on your WiFi")
    print(f"   2. Share this URL: http://{local_ip}:5000")
    print("   3. They create accounts and join your study groups")
    print()
    
    print("OPTION 2: ngrok Internet Tunnel (Recommended)")
    print("-" * 50)
    print("✅ Best for: Friends anywhere in the world")
    print("✅ Secure HTTPS connection")
    print("✅ No router configuration needed")
    download_ngrok()
    print()
    
    print("OPTION 3: Port Forwarding (Advanced)")
    print("-" * 40)
    print("⚠️  Best for: Tech-savvy users")
    print("⚠️  Security risk - only for trusted friends")
    print("📋 Steps:")
    print("   1. Log into router (usually 192.168.1.1)")
    print("   2. Find 'Port Forwarding' settings")
    print("   3. Forward port 5000 to your computer")
    print(f"   4. Friends use: http://{public_ip}:5000")
    print()
    
    # Quick actions
    print("🔧 QUICK ACTIONS:")
    print("=" * 20)
    
    if not server_running:
        print("🚀 Start Server:")
        print("   python intelliplan.py")
        print()
    
    if not firewall_ok and platform.system() == "Windows":
        print("🔥 Fix Firewall (run as Administrator):")
        choice = input("Add firewall rule now? (y/n): ").lower()
        if choice == 'y':
            if setup_firewall():
                print("✅ Firewall rule added successfully!")
            else:
                print("❌ Failed to add firewall rule. Run as Administrator.")
        print()
    
    print("🧪 Test Connection:")
    if server_running:
        test_url = f"http://{local_ip}:5000/connection-test"
        print(f"   Visit: {test_url}")
        choice = input("Open connection test page? (y/n): ").lower()
        if choice == 'y':
            webbrowser.open(test_url)
    else:
        print("   Start server first, then visit /connection-test")
    print()
    
    print("✅ SETUP COMPLETE!")
    print("=" * 20)
    print("Your Intelliplan app is configured for cross-device access.")
    print("Choose the option that works best for your situation.")
    print()
    print("💡 TIP: For the best experience, use ngrok for internet access")
    print("    or same-WiFi access for local friends.")

if __name__ == "__main__":
    main()
