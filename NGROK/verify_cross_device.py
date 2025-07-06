#!/usr/bin/env python3
"""
INTELLIPLAN CROSS-DEVICE VERIFICATION SCRIPT
============================================

This script tests all aspects of cross-device functionality
to ensure friends with different IP addresses can access your app.
"""

import socket
import requests
import time
import json
import platform
import subprocess
from urllib.parse import urljoin

class CrossDeviceTest:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.local_ip = self.get_local_ip()
        self.results = []
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def test_server_accessibility(self):
        """Test server accessibility from different addresses"""
        print("🌐 Testing Server Accessibility...")
        print("-" * 40)
        
        test_urls = [
            ("Localhost", "http://localhost:5000"),
            ("127.0.0.1", "http://127.0.0.1:5000"),
            (f"Local IP", f"http://{self.local_ip}:5000")
        ]
        
        all_passed = True
        for name, url in test_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name}: ACCESSIBLE")
                    self.results.append(f"✅ {name}: Working")
                else:
                    print(f"❌ {name}: HTTP {response.status_code}")
                    self.results.append(f"❌ {name}: HTTP Error")
                    all_passed = False
            except requests.exceptions.ConnectionError:
                print(f"❌ {name}: CONNECTION REFUSED")
                self.results.append(f"❌ {name}: Server not running")
                all_passed = False
            except requests.exceptions.Timeout:
                print(f"❌ {name}: TIMEOUT")
                self.results.append(f"❌ {name}: Timeout")
                all_passed = False
            except Exception as e:
                print(f"❌ {name}: ERROR - {str(e)}")
                self.results.append(f"❌ {name}: Error")
                all_passed = False
        
        print()
        return all_passed
    
    def test_socketio_endpoint(self):
        """Test Socket.IO endpoint specifically"""
        print("🔌 Testing Socket.IO Endpoint...")
        print("-" * 35)
        
        socketio_urls = [
            f"http://localhost:5000/socket.io/",
            f"http://{self.local_ip}:5000/socket.io/"
        ]
        
        all_passed = True
        for url in socketio_urls:
            try:
                response = requests.get(url, timeout=3)
                # Socket.IO endpoint returns 400 for GET requests, which is expected
                if response.status_code in [200, 400]:
                    print(f"✅ Socket.IO at {url}: WORKING")
                    self.results.append("✅ Socket.IO: Working")
                else:
                    print(f"❌ Socket.IO at {url}: HTTP {response.status_code}")
                    all_passed = False
            except Exception as e:
                print(f"❌ Socket.IO at {url}: ERROR")
                all_passed = False
        
        print()
        return all_passed
    
    def test_configuration(self):
        """Test Flask app configuration"""
        print("⚙️  Testing Flask Configuration...")
        print("-" * 35)
        
        config_file = "intelliplan.py"
        required_configs = {
            "External Host": "host='0.0.0.0'",
            "CORS Origins": 'cors_allowed_origins="*"',
            "Socket.IO Config": "SocketIO(",
            "Transport Config": "transports="
        }
        
        all_passed = True
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for name, config in required_configs.items():
                if config in content:
                    print(f"✅ {name}: CONFIGURED")
                    self.results.append(f"✅ {name}: OK")
                else:
                    print(f"❌ {name}: MISSING")
                    self.results.append(f"❌ {name}: Missing")
                    all_passed = False
        
        except FileNotFoundError:
            print("❌ intelliplan.py not found")
            all_passed = False
        
        print()
        return all_passed
    
    def test_firewall(self):
        """Test Windows Firewall settings"""
        print("🔥 Testing Firewall Settings...")
        print("-" * 30)
        
        if platform.system() != "Windows":
            print("⚠️  Firewall test skipped (not Windows)")
            print()
            return True
        
        try:
            result = subprocess.run(
                ["netsh", "advfirewall", "firewall", "show", "rule", "name=Intelliplan"],
                capture_output=True, text=True, timeout=10
            )
            
            if "Intelliplan" in result.stdout:
                print("✅ Firewall rule exists: Intelliplan")
                self.results.append("✅ Firewall: Configured")
                return True
            else:
                print("❌ Firewall rule missing")
                print("   Run this as Administrator:")
                print('   netsh advfirewall firewall add rule name="Intelliplan" dir=in action=allow port=5000 protocol=TCP')
                self.results.append("❌ Firewall: Not configured")
                return False
        
        except Exception as e:
            print(f"⚠️  Could not check firewall: {str(e)}")
            self.results.append("⚠️  Firewall: Unknown")
            return True
        
        print()
    
    def test_connection_page(self):
        """Test the connection test page"""
        print("🧪 Testing Connection Test Page...")
        print("-" * 35)
        
        test_url = f"http://{self.local_ip}:5000/connection-test"
        try:
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Connection test page: WORKING")
                print(f"   URL: {test_url}")
                self.results.append("✅ Test page: Working")
                return True
            else:
                print(f"❌ Connection test page: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection test page: ERROR")
            return False
        
        print()
    
    def generate_report(self):
        """Generate final report"""
        print("📊 CROSS-DEVICE TEST REPORT")
        print("=" * 50)
        print()
        
        print("📍 Network Information:")
        print(f"   Local IP: {self.local_ip}")
        print(f"   Test URLs:")
        print(f"     • http://localhost:5000")
        print(f"     • http://{self.local_ip}:5000")
        print()
        
        print("📋 Test Results:")
        for result in self.results:
            print(f"   {result}")
        print()
        
        # Count passed tests
        passed = len([r for r in self.results if r.startswith("✅")])
        total = len(self.results)
        
        print(f"📊 Summary: {passed}/{total} tests passed")
        print()
        
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
            print("   Your Intelliplan app is ready for cross-device access.")
            print()
            print("📱 Next Steps:")
            print("   1. Friends on same WiFi can use:")
            print(f"      http://{self.local_ip}:5000")
            print()
            print("   2. For internet access, use ngrok:")
            print("      • Download from https://ngrok.com/")
            print("      • Run: ngrok http 5000")
            print("      • Share the ngrok URL with friends")
        else:
            print("⚠️  SOME TESTS FAILED")
            print("   Please fix the issues above before sharing with friends.")
            print()
            print("🔧 Common Solutions:")
            print("   • Start server: python intelliplan.py")
            print("   • Fix firewall: Run as Administrator")
            print("   • Check router settings for device isolation")
        
        print()
        print("=" * 50)
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧠 INTELLIPLAN CROSS-DEVICE VERIFICATION")
        print("=" * 50)
        print()
        
        tests = [
            self.test_server_accessibility,
            self.test_socketio_endpoint,
            self.test_configuration,
            self.test_firewall,
            self.test_connection_page
        ]
        
        for test in tests:
            test()
            time.sleep(1)  # Brief pause between tests
        
        self.generate_report()

def main():
    tester = CrossDeviceTest()
    tester.run_all_tests()
    
    # Keep window open
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
