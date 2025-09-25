#!/usr/bin/env python3
"""
Comprehensive API Test Suite for AI Studio
Tests all major endpoints and functionality
"""

import requests
import json
import time
import uuid
from typing import Dict, Any
from datetime import datetime
import sys
import os

# Add Backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user = None
        self.access_token = None
        self.test_results = []

    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "response": response_data
        }
        self.test_results.append(result)

        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")

    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"

        # Add auth header if we have a token
        if self.access_token:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.access_token}'
            kwargs['headers'] = headers

        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n🏥 Testing Health Endpoints")

        # Test basic health
        try:
            response = self.make_request("GET", "/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}")
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", False, str(e))

        # Test API health
        try:
            response = self.make_request("GET", "/api/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Health Check", True, f"Status: {data.get('status')}")
            else:
                self.log_test("API Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("API Health Check", False, str(e))

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints")

        # Test registration
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        test_username = f"testuser_{uuid.uuid4().hex[:8]}"
        test_password = "TestPass123!"

        try:
            response = self.make_request("POST", "/api/auth/register", json={
                "email": test_email,
                "username": test_username,
                "password": test_password,
                "full_name": "Test User"
            })

            if response.status_code == 201:
                data = response.json()
                self.access_token = data.get('access_token')
                self.test_user = {
                    "email": test_email,
                    "username": test_username,
                    "user_id": data.get('user', {}).get('id')
                }
                self.log_test("User Registration", True, f"User: {test_username}")
            else:
                self.log_test("User Registration", False, f"Status: {response.status_code}", response.json())
        except Exception as e:
            self.log_test("User Registration", False, str(e))

        # Test login
        if self.test_user:
            try:
                response = self.make_request("POST", "/api/auth/login", json={
                    "email": test_email,
                    "password": test_password
                })

                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get('access_token')
                    self.log_test("User Login", True, f"User: {test_username}")
                else:
                    self.log_test("User Login", False, f"Status: {response.status_code}", response.json())
            except Exception as e:
                self.log_test("User Login", False, str(e))

        # Test get current user
        if self.access_token:
            try:
                response = self.make_request("GET", "/api/auth/me")
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Get Current User", True, f"User: {data.get('username')}")
                else:
                    self.log_test("Get Current User", False, f"Status: {response.status_code}", response.json())
            except Exception as e:
                self.log_test("Get Current User", False, str(e))

    def test_chat_endpoints(self):
        """Test chat functionality"""
        print("\n💬 Testing Chat Endpoints")

        if not self.access_token:
            self.log_test("Chat Endpoints", False, "No auth token available - skipping chat tests")
            return

        # Create a chat session
        try:
            response = self.make_request("POST", "/api/chat/sessions", json={
                "name": "Test Session",
                "model_config": {
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            })

            if response.status_code == 200:
                data = response.json()
                session_id = data.get('id')
                self.log_test("Create Chat Session", True, f"Session ID: {session_id}")

                # Test chat completion
                try:
                    response = self.make_request("POST", "/api/chat/chat", json={
                        "message": "Hello! Can you help me write a simple Python function?",
                        "session_id": session_id,
                        "model_config": {
                            "temperature": 0.7,
                            "max_tokens": 100
                        }
                    })

                    if response.status_code == 200:
                        data = response.json()
                        self.log_test("Chat Completion", True, f"Response length: {len(data.get('message', ''))}")
                    else:
                        self.log_test("Chat Completion", False, f"Status: {response.status_code}", response.json())
                except Exception as e:
                    self.log_test("Chat Completion", False, str(e))

                # Test get sessions
                try:
                    response = self.make_request("GET", "/api/chat/sessions")
                    if response.status_code == 200:
                        data = response.json()
                        self.log_test("Get Chat Sessions", True, f"Sessions count: {len(data)}")
                    else:
                        self.log_test("Get Chat Sessions", False, f"Status: {response.status_code}", response.json())
                except Exception as e:
                    self.log_test("Get Chat Sessions", False, str(e))

            else:
                self.log_test("Create Chat Session", False, f"Status: {response.status_code}", response.json())
        except Exception as e:
            self.log_test("Chat Endpoints", False, str(e))

    def test_code_execution(self):
        """Test code execution functionality"""
        print("\n🐍 Testing Code Execution")

        if not self.access_token:
            self.log_test("Code Execution", False, "No auth token available - skipping code tests")
            return

        try:
            response = self.make_request("POST", "/api/code/execute", json={
                "code": 'print("Hello World")\nprint("2 + 2 =", 2 + 2)',
                "language": "python",
                "timeout": 10
            })

            if response.status_code == 200:
                data = response.json()
                self.log_test("Code Execution", True, f"Status: {data.get('status')}")
            else:
                self.log_test("Code Execution", False, f"Status: {response.status_code}", response.json())
        except Exception as e:
            self.log_test("Code Execution", False, str(e))

    def test_rag_endpoints(self):
        """Test RAG functionality"""
        print("\n📚 Testing RAG Endpoints")

        if not self.access_token:
            self.log_test("RAG Endpoints", False, "No auth token available - skipping RAG tests")
            return

        # Test document upload (this might fail if no file is provided, but we can test the endpoint)
        try:
            response = self.make_request("GET", "/api/rag/documents")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Documents", True, f"Documents count: {len(data)}")
            else:
                self.log_test("Get Documents", False, f"Status: {response.status_code}", response.json())
        except Exception as e:
            self.log_test("Get Documents", False, str(e))

    def test_voice_endpoints(self):
        """Test voice functionality"""
        print("\n🎤 Testing Voice Endpoints")

        if not self.access_token:
            self.log_test("Voice Endpoints", False, "No auth token available - skipping voice tests")
            return

        try:
            response = self.make_request("GET", "/api/voice/speech-to-text")
            # This might fail as it expects audio data, but we can test if the endpoint exists
            if response.status_code in [200, 400, 405]:  # 400/405 expected for GET request to POST endpoint
                self.log_test("Voice Endpoint Available", True, f"Status: {response.status_code}")
            else:
                self.log_test("Voice Endpoint Available", False, f"Status: {response.status_code}", response.json())
        except Exception as e:
            self.log_test("Voice Endpoint Available", False, str(e))

    def test_image_generation(self):
        """Test image generation functionality"""
        print("\n🎨 Testing Image Generation")

        if not self.access_token:
            self.log_test("Image Generation", False, "No auth token available - skipping image tests")
            return

        try:
            response = self.make_request("POST", "/api/image/generate", json={
                "prompt": "A beautiful sunset over mountains",
                "width": 512,
                "height": 512,
                "style": "realistic"
            })

            if response.status_code == 200:
                data = response.json()
                self.log_test("Image Generation", True, "Image generated successfully")
            else:
                self.log_test("Image Generation", False, f"Status: {response.status_code}", response.json())
        except Exception as e:
            self.log_test("Image Generation", False, str(e))

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Generating Test Report")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        success_rate = (passed_tests/total_tests)*100 if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")

        # Save detailed report
        report_file = f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate,
                    "timestamp": datetime.now().isoformat()
                },
                "results": self.test_results
            }, f, indent=2)

        print(f"📄 Detailed report saved to: {report_file}")

        # Print failed tests
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")

        return passed_tests == total_tests

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive API Test Suite")
        print("=" * 60)

        try:
            self.test_health_endpoints()
            self.test_auth_endpoints()
            self.test_chat_endpoints()
            self.test_code_execution()
            self.test_rag_endpoints()
            self.test_voice_endpoints()
            self.test_image_generation()

            return self.generate_report()

        except KeyboardInterrupt:
            print("\n⏹️ Tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n💥 Test suite failed with error: {e}")
            return False

def main():
    """Main function"""
    print("🧪 AI Studio - Comprehensive API Test Suite")
    print("=" * 60)

    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not responding properly")
            print("Please make sure the backend server is running on http://localhost:8000")
            return 1
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to backend server")
        print("Please make sure the backend server is running on http://localhost:8000")
        return 1

    # Run tests
    tester = APITester()
    success = tester.run_all_tests()

    if success:
        print("\n🎉 All tests passed! Your API is working correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the report for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
