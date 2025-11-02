"""
OpenRouter Client for Dataset Generation
Uses GPT-4o-mini for high-quality, low-cost generation
"""

import json
import requests
import time
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class OpenRouterConfig:
    api_key: str = "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"
    base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    model: str = "openai/gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 4000
    
class OpenRouterClient:
    def __init__(self, config: OpenRouterConfig = None):
        self.config = config or OpenRouterConfig()
        
    def generate(self, 
                 messages: List[Dict[str, str]], 
                 temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None,
                 max_retries: int = 3) -> str:
        """Generate completion using OpenRouter API with Azure preference and retry logic"""
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://all1e.com",
            "X-Title": "ALL1E Dataset Generation v2.0 - Optimized"
        }
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "provider": {
                "order": ["Azure", "OpenAI"],  # Prefer Azure (259.6 tps vs 62.74 tps)
                "require_parameters": False
            }
        }
        
        last_error = None
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.config.base_url,
                    headers=headers,
                    json=payload,
                    timeout=60  # Reduced from 120s
                )
                response.raise_for_status()
                
                # Check rate limits and slow down if needed
                if 'x-ratelimit-remaining' in response.headers:
                    remaining = int(response.headers.get('x-ratelimit-remaining', 100))
                    if remaining < 10:
                        time.sleep(2)  # Slow down near limit
                
                result = response.json()
                return result['choices'][0]['message']['content']
                
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"⚠️ Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ OpenRouter API error after {max_retries} attempts: {str(e)}")
                    if hasattr(e, 'response') and e.response is not None:
                        print(f"   Response: {e.response.text}")
        
        raise last_error if last_error else Exception("Unknown error")
    
    def test_connection(self) -> bool:
        """Test OpenRouter connection"""
        try:
            messages = [{"role": "user", "content": "Rispondi solo 'OK' per confermare connessione."}]
            response = self.generate(messages, max_tokens=10)
            print(f"✅ OpenRouter connection successful: {response}")
            return True
        except Exception as e:
            print(f"❌ OpenRouter connection failed: {str(e)}")
            return False

if __name__ == "__main__":
    # Test connection
    client = OpenRouterClient()
    client.test_connection()
