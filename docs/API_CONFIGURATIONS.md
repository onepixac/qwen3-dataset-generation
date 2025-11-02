# API Configurations

> Complete API settings, keys, models, and rate limits for dataset generation

## 📊 Overview

All generators use the **OpenRouter API** as a unified gateway for Claude Haiku 4.5.

**Why OpenRouter?**
- ✅ Single API for multiple providers
- ✅ Automatic failover
- ✅ Better rate limits
- ✅ Cost optimization
- ✅ Usage analytics

---

## 🔑 API Keys

### Required Environment Variables

```bash
# .env file
OPENROUTER_API_KEY="sk-or-v1-..."  # Required for all generators
OPENAI_API_KEY="sk-proj-..."       # Optional, only for formulas (GPT-4o)
HF_TOKEN="hf_..."                  # Optional, for formula validation
```

### Get API Keys

**OpenRouter** (Primary):
1. Visit https://openrouter.ai/
2. Sign up / Log in
3. Go to **Keys** section
4. Create new API key
5. Copy and save securely

**OpenAI** (Formulas only):
1. Visit https://platform.openai.com/
2. Go to API Keys
3. Create new secret key
4. Copy and save

**HuggingFace** (Optional):
1. Visit https://huggingface.co/settings/tokens
2. Create new token with "Read" access
3. Copy and save

---

## 🤖 Models

### Primary Model (All Generators)

```python
MODEL = "anthropic/claude-3.5-haiku"

# Via OpenRouter
BASE_URL = "https://openrouter.ai/api/v1"
```

**Specifications**:
- **Context Window**: 200,000 tokens
- **Max Output**: 8,192 tokens
- **Temperature Range**: 0.0 - 1.0
- **Languages**: Multilingual (optimized for Italian)
- **Speed**: ~2.5 seconds per response (average)

**Pricing (OpenRouter)**:
- **Input**: $0.25 per 1M tokens
- **Output**: $1.25 per 1M tokens
- **Effective**: ~$2.60 per 1,000 examples

### Alternative Model (Formulas Only)

```python
MODEL = "gpt-4o"  # OpenAI direct

# For LaTeX formula generation
BASE_URL = "https://api.openai.com/v1"
```

**Specifications**:
- **Context Window**: 128,000 tokens
- **Max Output**: 16,384 tokens
- **Best for**: Mathematical notation, LaTeX rendering

**Pricing (OpenAI)**:
- **Input**: $2.50 per 1M tokens
- **Output**: $10.00 per 1M tokens
- **Usage**: Only 207 examples (formulas)

---

## ⚙️ Sampling Parameters

### Default Configuration

```python
# Applied to all generators
SAMPLING_CONFIG = {
    "temperature": 0.9,       # High creativity for diverse examples
    "top_p": 0.95,            # Nucleus sampling
    "frequency_penalty": 0.1, # Reduce repetition
    "presence_penalty": 0.1,  # Encourage topic diversity
    "max_tokens": 6000        # Long responses for education
}
```

### Per-Task Adjustments

```python
# Chat/RAG: High creativity
CHAT_TEMPERATURE = 0.9
CHAT_MAX_TOKENS = 6000

# Quiz: Moderate creativity (need consistency)
QUIZ_TEMPERATURE = 0.8
QUIZ_MAX_TOKENS = 4000

# Citations: Focused (need accuracy)
CITATIONS_TEMPERATURE = 0.7
CITATIONS_MAX_TOKENS = 5000

# Cloze: Very focused (specific blanks)
CLOZE_TEMPERATURE = 0.6
CLOZE_MAX_TOKENS = 3000

# Reasoning: Balanced
REASONING_TEMPERATURE = 0.8
REASONING_MAX_TOKENS = 5000

# Function Calling: Precise (JSON structure)
FUNCTION_TEMPERATURE = 0.7
FUNCTION_MAX_TOKENS = 4000
```

---

## 🚦 Rate Limits

### OpenRouter Limits

```python
# Per-model rate limits
CLAUDE_HAIKU_LIMITS = {
    "requests_per_minute": 500,
    "tokens_per_minute": 100000,
    "concurrent_requests": 100
}
```

### Our Usage (Conservative)

```python
# v2.0 - v2.4
MAX_CONCURRENT = 30        # 270 req/min (54% of limit)
BATCH_DELAY_MS = 500       # Rate limiting between batches

# v2.5 - v2.7 (Optimized)
MAX_CONCURRENT = 45        # 270 req/min (54% of limit)
BATCH_DELAY_MS = 500       # Same safety margin
```

**Safety Calculation**:
```
45 concurrent requests × 60 seconds / 60 seconds = 45 req/s
45 req/s × 60 = 2,700 req/min WITHOUT delays

With 500ms batch delays (100 examples per batch):
Real throughput: ~270 req/min (54% of 500 limit) ✅
```

### Rate Limit Handling

```python
async def api_call_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = await client.chat_completion(prompt)
            return response
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
            else:
                log_error("Rate limit exceeded after retries")
                return None
```

---

## 💰 Cost Optimization

### Strategies

**1. Batch Similar Requests**
```python
# Instead of 1 request with 6000 tokens output
# Use 2 requests with 3000 tokens each
# Cost: Same, but faster generation
```

**2. Progressive Temperature**
```python
# Start with high temperature (0.9) for first 80%
# Lower to 0.7 for last 20% to ensure quality
```

**3. Smart Retry Logic**
```python
# Only retry on network errors, not validation errors
if error.type in ["timeout", "connection"]:
    retry()
else:
    skip_and_log()  # Don't waste API calls
```

**4. Caching Prompts**
```python
# Cache system prompts (reused across examples)
# OpenRouter may cache on their side
# Reduces input token costs
```

### Cost Monitoring

```python
# Track in real-time
cost_tracker = {
    "input_tokens": 0,
    "output_tokens": 0,
    "total_cost": 0.0
}

def update_cost(input_tokens, output_tokens):
    cost_tracker["input_tokens"] += input_tokens
    cost_tracker["output_tokens"] += output_tokens
    
    input_cost = input_tokens * 0.25 / 1_000_000
    output_cost = output_tokens * 1.25 / 1_000_000
    
    cost_tracker["total_cost"] += input_cost + output_cost
    
    print(f"💰 Cost so far: ${cost_tracker['total_cost']:.2f}")
```

---

## 🔐 Security

### API Key Management

**DO NOT**:
- ❌ Commit `.env` files to git
- ❌ Hardcode API keys in scripts
- ❌ Share API keys in logs
- ❌ Use same key across projects

**DO**:
- ✅ Use environment variables
- ✅ Add `.env` to `.gitignore`
- ✅ Rotate keys periodically
- ✅ Use project-specific keys

### .gitignore

```gitignore
# API Keys
.env
.env.local
*.key

# Logs (may contain API responses)
logs/
*.log

# Checkpoints (may contain API data)
checkpoints/
```

### Environment Loading

```python
# openrouter_client.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment")
```

---

## 📊 Usage Analytics

### OpenRouter Dashboard

Access real-time analytics:
1. Visit https://openrouter.ai/activity
2. View requests, costs, errors
3. Download usage reports

**Metrics Available**:
- Requests per hour/day/week
- Token usage (input/output)
- Cost breakdown by model
- Error rates and types
- Latency percentiles

### Custom Tracking

```python
# Track in code
import json
from datetime import datetime

usage_log = {
    "timestamp": datetime.utcnow().isoformat(),
    "generator": "v2.5_emotional_support",
    "stats": {
        "requests": 20508,
        "input_tokens": 10254000,
        "output_tokens": 51270000,
        "cost_usd": 17.12,
        "duration_hours": 5.2
    }
}

with open("usage_log.json", "a") as f:
    f.write(json.dumps(usage_log) + "\n")
```

---

## 🔧 Configuration Files

### openrouter_client.py

```python
import os
from openai import AsyncOpenAI

class OpenRouterClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        
    async def chat_completion(
        self,
        messages: list,
        model: str = "anthropic/claude-3.5-haiku",
        temperature: float = 0.9,
        max_tokens: int = 6000,
        top_p: float = 0.95
    ):
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                extra_headers={
                    "HTTP-Referer": "https://all1e.com",
                    "X-Title": "ALL1E Dataset Generation"
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            raise e
```

### Environment Template (.env.example)

```bash
# OpenRouter API (Required)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# OpenAI API (Optional - only for formulas)
OPENAI_API_KEY=sk-proj-your-key-here

# HuggingFace Token (Optional - for validation)
HF_TOKEN=hf_your_token_here

# Configuration
MAX_CONCURRENT=45
BATCH_DELAY_MS=500
TEMPERATURE=0.9
MAX_TOKENS=6000
```

---

## 🚀 Best Practices

1. **Always Use Environment Variables**
   ```python
   API_KEY = os.getenv("OPENROUTER_API_KEY")
   ```

2. **Monitor Costs in Real-Time**
   ```python
   print(f"💰 Current cost: ${total_cost:.2f}")
   ```

3. **Implement Retry Logic**
   ```python
   for attempt in range(3):
       try:
           response = await api_call()
           break
       except RateLimitError:
           await asyncio.sleep(2 ** attempt)
   ```

4. **Log API Errors**
   ```python
   try:
       response = await api_call()
   except Exception as e:
       log_error(f"API error: {e}")
   ```

5. **Use Batch Delays**
   ```python
   await asyncio.sleep(BATCH_DELAY_MS / 1000)
   ```

---

## 📞 Support

- **OpenRouter**: https://openrouter.ai/docs
- **OpenAI**: https://platform.openai.com/docs
- **HuggingFace**: https://huggingface.co/docs

---

**Last Updated**: 2025-11-02 | **Version**: 1.0.0
