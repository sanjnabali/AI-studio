# Save as Backend/test_services.py
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"✅ Health: {response.status_code} - {response.json().get('status', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    print("\n💬 Testing chat endpoint...")
    try:
        payload = {
            "messages": [
                {"role": "user", "content": "Hello! Can you help me write a Python function?"}
            ],
            "domain": "code",
            "temperature": 0.7
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=15)
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat response ({latency:.1f}ms): {result.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def test_code_execution():
    """Test code execution"""
    print("\n🐍 Testing code execution...")
    try:
        payload = {
            "code": 'print("Hello from Python!")\nprint("2 + 2 =", 2 + 2)',
            "language": "python",
            "timeout": 10
        }
        
        response = requests.post(f"{BASE_URL}/api/execute-code", json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Code execution successful:")
                print(f"   Output: {result.get('output', '').strip()}")
                print(f"   Time: {result.get('execution_time', 0):.2f}s")
                return True
            else:
                print(f"❌ Code execution failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Code execution request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Code execution test failed: {e}")
        return False

def test_voice_health():
    """Test voice service health"""
    print("\n🎤 Testing voice service...")
    try:
        response = requests.get(f"{BASE_URL}/api/voice-to-text/health", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Voice service: {result.get('status', 'unknown')}")
            print(f"   Supported formats: {result.get('supported_formats', [])}")
            return True
        else:
            print(f"❌ Voice service health failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Voice service test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing AI Studio Backend Services")
    print("=" * 50)
    
    tests = [
        test_health,
        test_chat, 
        test_code_execution,
        test_voice_health
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except KeyboardInterrupt:
            print("\n⏹️ Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is working correctly.")
    elif passed > total // 2:
        print("⚠️ Most tests passed. Some features may need attention.")
    else:
        print("❌ Multiple tests failed. Check your backend configuration.")
    
    return passed == total

if __name__ == "__main__":
    main()