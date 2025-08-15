#!/usr/bin/env python3
"""
Test the improved mock LLM with navigation responses
"""
import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from backend.app.llm.client import chat_completion

# Test visual navigation response
print("🧪 Testing Mock LLM Navigation Response:")
response = chat_completion(
    "You are a navigation AI for a virtual character in an OPEN-TOP HOUSE simulation. Return STRICT JSON only.",
    "I can see the character and need to move toward the kitchen.",
    100
)
print(f"📍 Navigation Response: {response}")
print("✅ Mock LLM is ready for Blender addon!")
