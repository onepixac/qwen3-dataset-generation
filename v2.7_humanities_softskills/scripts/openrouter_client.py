"""
OpenRouter API Client for Gap Filling Generation
Uses Claude Haiku 4.5 for high-quality educational content
"""

import json
import time
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class OpenRouterConfig:
    """Configuration for OpenRouter API - Claude Haiku 4.5"""
    api_key: str = "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"
    base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    model: str = "anthropic/claude-haiku-4.5"  # Claude Haiku 4.5 for top-tier quality
    temperature: float = 0.7
    max_tokens: int = 16384  # Increased for 12 Q&A with long answers
    timeout: int = 120


class OpenRouterClient:
    """Client for OpenRouter API with Claude Haiku 4.5"""

    def __init__(self, config: Optional[OpenRouterConfig] = None):
        self.config = config or OpenRouterConfig()

    def generate_json(self, prompt: str, max_retries: int = 3) -> List[Dict]:
        """Generate JSON response from OpenRouter API"""
        for attempt in range(max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://all1e.com",
                    "X-Title": "ALL1E Gap Filling Generation"
                }

                payload = {
                    "model": self.config.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens
                }

                response = requests.post(
                    self.config.base_url,
                    headers=headers,
                    json=payload,
                    timeout=self.config.timeout
                )

                response.raise_for_status()
                result = response.json()

                # Extract content from response
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                if not content:
                    print(f"   ⚠️ Empty content on attempt {attempt + 1}")
                    time.sleep(2)
                    continue

                # Parse JSON from content
                # Try to find JSON block (might be wrapped in markdown)
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                # Parse JSON
                try:
                    data = json.loads(content)

                    # Validate structure
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and "conversations" in data:
                        return data["conversations"]
                    else:
                        print(f"   ⚠️ Unexpected JSON structure on attempt {attempt + 1}")
                        time.sleep(2)
                        continue

                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON parse error: {e}")
                    print(f"   Response preview: {content[:200]}...")
                    time.sleep(2)
                    continue

            except requests.exceptions.Timeout:
                print(f"   ⏱️ Timeout on attempt {attempt + 1}")
                time.sleep(5)
                continue

            except requests.exceptions.RequestException as e:
                print(f"   ❌ Request error on attempt {attempt + 1}: {e}")
                time.sleep(5)
                continue

            except Exception as e:
                print(f"   ❌ Exception: {e}")
                time.sleep(5)
                continue

        # All retries failed
        return []

    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            result = self.generate_json("Say 'Hello, I am Claude Haiku 4.5!' in Italian.", max_retries=1)
            return len(result) > 0
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


if __name__ == "__main__":
    # Test the client
    print("🔧 Testing OpenRouter Client with Claude Haiku 4.5...")
    client = OpenRouterClient()

    if client.test_connection():
        print("✅ Connection successful!")
    else:
        print("❌ Connection failed!")
