#!/usr/bin/env python3
"""
Simple test for OpenAI client configuration following the OpenAI Python library documentation.
Tests the LLM connection with the corrected URL: http://100.98.151.66:1234/v1
"""
import os
import httpx
from dotenv import load_dotenv
from openai import OpenAI, DefaultHttpxClient

# Load environment variables
load_dotenv()

def test_openai_client():
    """Test OpenAI client with the corrected configuration."""
    
    # Configuration - using the corrected URL
    BASE_URL = "http://100.98.151.66:1234/v1"
    API_KEY = "sk-a6af2053d49649d2925ff91fef71cb65"
    MODEL = "openai/gpt-oss-120b"
    TIMEOUT = 30.0
    
    print("🧪 Testing OpenAI Client Configuration")
    print("=" * 50)
    print(f"Base URL: {BASE_URL}")
    print(f"Model: {MODEL}")
    print(f"Timeout: {TIMEOUT}s")
    print()
    
    try:
        # Create OpenAI client following the documentation pattern
        print("Creating OpenAI client with custom httpx configuration...")
        client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY,
            http_client=DefaultHttpxClient(
                transport=httpx.HTTPTransport(local_address="0.0.0.0"),
                timeout=TIMEOUT
            ),
        )
        print("✅ Client created successfully")
        
        # Test chat completion
        print("\n🔄 Testing chat completion...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello! OpenAI client is working correctly.' in one sentence."},
            ],
            max_tokens=50,
        )
        
        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content.strip()
            print(f"✅ SUCCESS: {content}")
            
            # Test models endpoint
            print("\n🔄 Testing models endpoint...")
            try:
                models_response = client.models.list()
                model_ids = [model.id for model in models_response.data]
                print(f"✅ Found {len(model_ids)} available models:")
                for model_id in model_ids[:3]:  # Show first 3 models
                    print(f"   - {model_id}")
                if len(model_ids) > 3:
                    print(f"   ... and {len(model_ids) - 3} more models")
                    
            except Exception as e:
                print(f"⚠️  Models endpoint failed (this is OK): {e}")
            
            print("\n🎉 OpenAI client test completed successfully!")
            print("The LLM connection is working with the corrected configuration.")
            return True
            
        else:
            print("❌ Empty response received")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\nTroubleshooting:")
        print("- Verify the server is running at http://100.98.151.66:1234")
        print("- Check network connectivity")
        print("- Ensure the API key is correct")
        return False

if __name__ == "__main__":
    success = test_openai_client()
    
    if success:
        print(f"\n✅ Test PASSED - OpenAI client configuration is working!")
    else:
        print(f"\n❌ Test FAILED - Check the configuration and server connection.")
    
    exit(0 if success else 1)
