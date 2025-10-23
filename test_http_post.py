import requests
import time

def test_http_post():
    """ทดสอบส่ง HTTP POST ไปยัง Django server"""
    
    url = "http://127.0.0.1:8000/simple/"
    
    print("=== HTTP POST Test ===")
    
    try:
        # ทดสอบ GET ก่อน
        print("🔍 Testing GET request...")
        get_response = requests.get(url, timeout=5)
        print(f"✅ GET Status: {get_response.status_code}")
        
        # ทดสอบ POST
        print("🚀 Testing POST request...")
        post_data = {'led_on': '1'}
        post_response = requests.post(url, data=post_data, timeout=5)
        print(f"✅ POST Status: {post_response.status_code}")
        print(f"📄 Response length: {len(post_response.text)}")
        
        # ทดสอบ POST อีกครั้งด้วย LED OFF
        print("🚀 Testing POST LED OFF...")
        post_data2 = {'led_off': '1'}
        post_response2 = requests.post(url, data=post_data2, timeout=5)
        print(f"✅ POST LED OFF Status: {post_response2.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("🔍 Is Django server running at http://127.0.0.1:8000/ ?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_http_post()
    print("🏁 Test completed!")