#!/usr/bin/env python3
"""
OpenAI client test with shorter timeouts to avoid hanging.
"""
import httpx
from openai import OpenAI, DefaultHttpxClient

def test_llm_with_openai_client():
    """Test LLM using OpenAI client with the solution from the GitHub documentation."""
    
    BASE_URL = "http://100.98.151.66:1234/v1"
    API_KEY = "sk-a6af2053d49649d2925ff91fef71cb65"
    MODEL = "openai/gpt-oss-120b"
    
    print("🚀 Testing OpenAI Client (with shorter timeout)")
    print("=" * 50)
    print(f"Base URL: {BASE_URL}")
    print(f"Model: {MODEL}")
    
    try:
        # Create OpenAI client exactly as shown in the GitHub documentation
        client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY,
            http_client=DefaultHttpxClient(
                transport=httpx.HTTPTransport(local_address="0.0.0.0"),
                timeout=10.0  # Shorter timeout
            ),
        )
        print("✅ OpenAI client created successfully")
        
        # Simple test message
        print("🔄 Sending test message...")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": "Hello, respond with just 'Working!' if you receive this."}
            ],
            max_tokens=10
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(f"✅ Response received: {content}")
            return True
        else:
            print("❌ No response content")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_llm_with_openai_client()
    
    print("\n" + "="*50)
    if success:
        print("🎉 SUCCESS: OpenAI client with custom httpx is working!")
        print("The LLM connection solution has been implemented correctly.")
    else:
        print("❌ FAILED: There's still an issue with the OpenAI client.")
        
    print(f"Exit code: {0 if success else 1}")
    exit(0 if success else 1)
