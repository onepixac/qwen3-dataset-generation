"""
OpenRouter API Client for v2.8 - GPT-4o-mini
Configured for Cinema & Media Studies dataset generation
"""

import os
import asyncio
from openai import AsyncOpenAI
from typing import List, Dict, Optional

class OpenRouterClient:
    """OpenRouter client using GPT-4o-mini for cost-effective generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client
        
        Args:
            api_key: OpenRouter API key (if not provided, reads from env)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found")
        
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        # GPT-4o-mini configuration
        self.model = "openai/gpt-4o-mini"
        self.default_temperature = 0.9
        self.default_max_tokens = 6000
        self.default_top_p = 0.95
        
        print(f"✅ OpenRouter client initialized")
        print(f"   Model: {self.model}")
        print(f"   Base URL: https://openrouter.ai/api/v1")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Generate chat completion
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (default: 0.9)
            max_tokens: Max tokens to generate (default: 6000)
            top_p: Nucleus sampling (default: 0.95)
            model: Model to use (default: gpt-4o-mini)
            
        Returns:
            Generated text content
        """
        try:
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature or self.default_temperature,
                max_tokens=max_tokens or self.default_max_tokens,
                top_p=top_p or self.default_top_p,
                extra_headers={
                    "HTTP-Referer": "https://all1e.com",
                    "X-Title": "ALL1E v2.8 Cinema Dataset Generation"
                }
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            raise e
    
    async def chat_completion_with_retry(
        self,
        messages: List[Dict[str, str]],
        max_retries: int = 3,
        **kwargs
    ) -> Optional[str]:
        """
        Generate with automatic retry on failure
        
        Args:
            messages: List of message dicts
            max_retries: Maximum retry attempts
            **kwargs: Additional arguments for chat_completion
            
        Returns:
            Generated text or None if all retries failed
        """
        for attempt in range(max_retries):
            try:
                result = await self.chat_completion(messages, **kwargs)
                return result
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"   ⚠️  Retry {attempt + 1}/{max_retries} after {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"   ❌ Failed after {max_retries} attempts")
                    return None
        
        return None

# Pricing information (GPT-4o-mini via OpenRouter)
PRICING = {
    "model": "openai/gpt-4o-mini",
    "input_cost_per_1m": 0.15,   # $0.15 per 1M tokens
    "output_cost_per_1m": 0.60,  # $0.60 per 1M tokens
    "notes": "~75% cheaper than Claude Haiku 4.5"
}

def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate generation cost in USD"""
    input_cost = (input_tokens / 1_000_000) * PRICING["input_cost_per_1m"]
    output_cost = (output_tokens / 1_000_000) * PRICING["output_cost_per_1m"]
    return input_cost + output_cost

if __name__ == "__main__":
    print("="*80)
    print("🎬 OpenRouter Client for v2.8 - GPT-4o-mini")
    print("="*80)
    print(f"\nModel: {PRICING['model']}")
    print(f"Input cost: ${PRICING['input_cost_per_1m']:.2f} / 1M tokens")
    print(f"Output cost: ${PRICING['output_cost_per_1m']:.2f} / 1M tokens")
    print(f"Note: {PRICING['notes']}")
    print("\n" + "="*80)
