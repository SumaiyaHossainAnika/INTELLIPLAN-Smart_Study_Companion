import requests

print("🔧 Ngrok vs Local Socket.IO Comparison")
print("=" * 50)

# Test both local and ngrok endpoints
endpoints = [
    ("Local", "http://localhost:5000"),
    ("Ngrok", "https://8fcd-45-127-246-48.ngrok-free.app")
]

socket_path = "/socket.io/?EIO=4&transport=polling"

for name, base_url in endpoints:
    try:
        url = f"{base_url}{socket_path}"
        print(f"\n🧪 Testing {name}: {url}")
        
        # Add ngrok headers if needed
        headers = {}
        if "ngrok" in base_url:
            headers["ngrok-skip-browser-warning"] = "true"
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print(f"   🎉 {name} Socket.IO is working!")
        else:
            print(f"   ❌ {name} Socket.IO failed")
            
    except Exception as e:
        print(f"   💥 {name} Error: {e}")

print("\n✨ Comparison completed!")
