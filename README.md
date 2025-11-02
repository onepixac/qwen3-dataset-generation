# Qwen3 Fine-tuning Dataset Generation

> Complete toolkit for generating high-quality Italian educational datasets using Claude Haiku 4.5 and GPT-4o

## 📊 Overview

This repository contains **all production scripts** used to generate **220,000+ training examples** for fine-tuning Qwen3-4B models for the ALL1E educational platform.

**Total Dataset**: 223,261 examples across 40+ distinct datasets (8 major versions) (v2.0 → v2.7 + formulas)

**Performance**:
- Generation cost: **~$600 USD** (Claude Haiku 4.5 API)
- Time: **~120 hours (distributed)** (with parallel processing)
- Success rate: **99.2%** (valid JSON responses)
- Quality: **Production-ready** (validated with 88.11% token accuracy)

---

## 🏗️ Architecture

### Data Generation Pipeline

```
Topic Seeds → Claude Haiku 4.5 API → JSON Validation → JSONL Output
                     ↓
          (45 parallel requests)
                     ↓
         Rate limiting (500ms delay)
                     ↓
        Auto-recovery on failures
```

### API Configuration

| API | Model | Purpose | Cost per 1M tokens |
|-----|-------|---------|---------------------|
| OpenRouter | Claude Haiku 4.5 | Primary generation | $0.25 / $1.25 |
| OpenAI | GPT-4o | Formula LaTeX | $2.50 / $10.00 |
| HuggingFace | Qwen/Qwen2.5-Math-7B | Formula validation | Free (Inference API) |

**Total API Cost**: ~$255 for 95K examples

---

## 📁 Repository Structure

```
qwen3-dataset-generation/
├── README.md                           # This file
├── v2.0_base/                          # Base dataset (25K examples)
│   ├── README.md                       # Detailed v2.0 documentation
│   ├── scripts/
│   │   ├── generator_chat_rag.py      # Chat/RAG generation
│   │   ├── generator_quiz_correct.py   # Quiz generation
│   │   ├── generator_citations.py      # Citations
│   │   ├── generator_cloze.py          # Cloze tests
│   │   ├── generator_reasoning.py      # Reasoning questions
│   │   ├── generator_function_calling.py # Function calling
│   │   └── master_generator.py         # Orchestrator
│   └── output/                         # Generated JSONL files
│
├── v2.1_medicina/                      # Medical specialization (18K)
│   ├── README.md
│   ├── scripts/
│   │   ├── generator_chat_medicina.py
│   │   ├── generator_quiz_medicina.py
│   │   └── ...
│   └── output/
│
├── v2.2_scienze/                       # Sciences (Biologia, Chimica, Fisica, Matematica)
│   ├── README.md                       # 10K examples
│   └── scripts/
│
├── v2.3_logica/                        # Logic & Critical Thinking
│   ├── README.md                       # 10K examples
│   └── scripts/
│
├── v2.4_ingegneria/                    # Engineering specialization
│   ├── README.md                       # 8K examples
│   └── scripts/
│
├── v2.5_emotional_support/             # Emotional intelligence
│   ├── README.md                       # 7K examples
│   └── scripts/
│
├── v2.6_tone_flexibility/              # Tone adaptation
│   ├── README.md                       # 16K examples (IN PROGRESS)
│   └── scripts/
│
├── v2.7_humanities_softskills/         # Humanities & Soft Skills
├──
├── preprocessing/                 # PDF chunk extraction & cleaning
│   ├── README.md
│   └── scripts/
│       ├── extract_and_clean_secrets.py
│       ├── extract_formula_chunks.py
│       └── extract_books_final.py
│
│   ├── README.md                       # 12K examples (IN PROGRESS)
│   └── scripts/
│
├── formulas/                           # LaTeX formula generation
│   ├── README.md                       # 207 examples
│   └── scripts/
│       ├── generator_formulas_gpt4o.py     # GPT-4o LaTeX
│       ├── generator_formulas_hf.py        # HuggingFace validation
│       └── generator_formulas_optimized.py # Production version
│
├── shared/                             # Shared utilities
│   ├── openrouter_client.py            # OpenRouter API client
│   └── start_all_generators.sh         # Parallel launcher
│
└── docs/
    ├── API_CONFIGURATIONS.md           # Complete API settings
    ├── BATCH_CONCURRENCY.md            # Performance tuning
    └── DATASET_SPECIFICATIONS.md       # Format specifications
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.10+
python3 --version

# Install dependencies
pip install openai anthropic requests tqdm
```

### Environment Variables

Create `.env` file:

```bash
# OpenRouter (Claude Haiku 4.5)
OPENROUTER_API_KEY="sk-or-v1-..."

# OpenAI (GPT-4o for formulas)
OPENAI_API_KEY="sk-proj-..."

# HuggingFace (optional, for formula validation)
HF_TOKEN="hf_..."
```

### Run Generation

```bash
# Single generator
cd v2.0_base/scripts
python3 generator_chat_rag.py

# Parallel execution (v2.5, v2.6, v2.7)
cd shared
chmod +x start_all_generators.sh
./start_all_generators.sh
```

---

## ⚙️ Configuration Matrix

### Batch Sizes & Concurrency

| Version | Topics | Examples/Topic | Batch Size | Concurrent API | Total Examples |
|---------|--------|----------------|------------|----------------|----------------|
| v2.0 | Mixed | Variable | 50-100 | 15-30 | 25,000 |
| v2.1 | 18 medical | 1,000 | 100 | 30 | 18,000 |
| v2.2 | 4 sciences | 2,500 | 100 | 30 | 10,000 |
| v2.3 | 10 logic | 1,000 | 100 | 30 | 10,000 |
| v2.4 | 8 engineering | 1,000 | 100 | 30 | 8,000 |
| v2.5 | 7 emotional | 1,000 | 100 | **45** | 7,000 |
| v2.6 | 13 tone | 1,250 | 150 | **45** | 16,250 |
| v2.7 | 12 humanities | 1,000 | 100 | **45** | 12,000 |
| Formulas | - | - | 10 | 5 | 207 |

**Key Optimizations (v2.5-v2.7)**:
- ✅ Increased concurrent API calls: 30 → **45** (+50%)
- ✅ Improved batch delays: 500ms → **300-500ms**
- ✅ Auto-recovery with exponential backoff
- ✅ Progress checkpointing every 100 examples

### API Rate Limits

| API | Rate Limit | Our Usage | Safety Margin |
|-----|------------|-----------|---------------|
| OpenRouter (Claude Haiku 4.5) | 500 req/min | 45 parallel (270/min) | ✅ 46% |
| OpenAI (GPT-4o) | 500 req/min | 5 parallel (30/min) | ✅ 94% |
| HuggingFace (Inference API) | 100 req/min | 5 parallel (30/min) | ✅ 70% |

---

## 📊 Dataset Statistics

### Final Dataset (Combined)

```json
{
  "total_examples": 95086,
  "versions": 8,
  "breakdown": {
    "v2.0_base": 25000,
    "v2.1_medicina": 18000,
    "v2.2_scienze": 10000,
    "v2.3_logica": 10000,
    "v2.4_ingegneria": 8000,
    "v2.5_emotional": 6836,
    "v2.6_tone": 16250,
    "v2.7_humanities": 12000,
    "formulas": 207
  },
  "formats": {
    "chat_rag": 45000,
    "quiz": 20000,
    "citations": 15000,
    "cloze": 8000,
    "reasoning": 7000,
    "function_calling": 3000,
    "formulas": 207
  },
  "languages": ["it"],
  "quality_metrics": {
    "json_validation": "99.2%",
    "token_accuracy": "88.11%",
    "production_ready": true
  }
}
```

### Training Results (Qwen3-4B)

**Model**: `qwen3_4b_reasoning_merged` (fine-tuned on 9.9K subset)

| Metric | Value |
|--------|-------|
| Training Loss | 0.4029 |
| Token Accuracy | 88.11% |
| Production Accuracy | >87% ✅ |
| Context Window | 32,768 tokens |
| Training Cost | $255 (dataset generation) |
| Training Time | 3 epochs (~12 hours on 4× L40S GPUs) |

---

## 🎯 Use Cases

### 1. Chat/RAG Responses
```json
{
  "messages": [
    {
      "role": "system",
      "content": "Sei ALL1E TUTOR, assistente educativo italiano..."
    },
    {
      "role": "user",
      "content": "Spiega il teorema di Pitagora con esempi pratici"
    },
    {
      "role": "assistant",
      "content": "Il teorema di Pitagora stabilisce che...\n\n**Esempio Pratico:**..."
    }
  ]
}
```

### 2. Quiz Generation
```json
{
  "messages": [
    {
      "role": "system",
      "content": "Sei ALL1E QUIZ GENERATOR..."
    },
    {
      "role": "user",
      "content": "[CHUNK: La fotosintesi clorofilliana...]"
    },
    {
      "role": "assistant",
      "content": "{\n  \"question\": \"Quale organulo...\",\n  \"options\": [...],\n  \"correct_answer\": 2\n}"
    }
  ]
}
```

### 3. Citations (RAG with Sources)
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Quali sono i sintomi dell'influenza?\n\nChunk 1: [SOURCE]..."
    },
    {
      "role": "assistant",
      "content": "I sintomi principali dell'influenza sono [1]:\n- Febbre alta [1][2]..."
    }
  ]
}
```

### 4. Function Calling
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Crea un grafico della funzione y = x^2"
    },
    {
      "role": "assistant",
      "content": "",
      "tool_calls": [
        {
          "type": "function",
          "function": {
            "name": "plotting_tool",
            "arguments": "{\"function\": \"x**2\", \"x_range\": [-10, 10]}"
          }
        }
      ]
    }
  ]
}
```

---

## 🔧 Technical Details

### Generator Architecture

All generators follow the same pattern:

```python
class Generator:
    def __init__(self):
        self.client = OpenRouterClient()  # Shared API client
        self.topics = load_topics()       # Topic seeds
        self.concurrent = 45              # Parallel requests
        self.batch_delay = 500            # ms between batches
        
    async def generate_topic(self, topic, target_count):
        """Generate examples for a single topic"""
        tasks = [
            self.generate_single(topic, i)
            for i in range(target_count)
        ]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]
        
    async def generate_single(self, topic, index):
        """Generate single example with retry"""
        for attempt in range(3):
            try:
                response = await self.client.chat_completion(
                    messages=[...],
                    model="anthropic/claude-3.5-haiku",
                    temperature=0.9,
                    max_tokens=6000
                )
                return self.validate_json(response)
            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    log_error(e)
                    return None
```

### Progress Tracking

All generators include:
- ✅ Real-time `tqdm` progress bars
- ✅ Checkpoint saving every 100 examples
- ✅ Auto-recovery from crashes
- ✅ JSON validation with detailed error logging
- ✅ Summary statistics on completion

### JSON Validation

```python
def validate_response(response: str) -> dict | None:
    """Validate API response is valid JSON with required fields"""
    try:
        data = json.loads(response)
        
        # Check required structure
        if "messages" not in data:
            return None
            
        # Validate message format
        for msg in data["messages"]:
            if "role" not in msg or "content" not in msg:
                return None
                
        return data
        
    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON: {e}")
        return None
```

---

## 📈 Performance & Cost

### Generation Performance

| Version | Examples | API Calls | Time | Cost |
|---------|----------|-----------|------|------|
| v2.0 | 25,000 | ~75,000 | 18h | $65 |
| v2.1 | 18,000 | ~54,000 | 12h | $47 |
| v2.2 | 10,000 | ~30,000 | 8h | $26 |
| v2.3 | 10,000 | ~30,000 | 8h | $26 |
| v2.4 | 8,000 | ~24,000 | 6h | $21 |
| v2.5 | 6,836 | ~20,000 | 5h | $17 |
| v2.6 | 16,250 | ~48,750 | 12h | $42 |
| v2.7 | 12,000 | ~36,000 | 9h | $31 |
| Formulas | 207 | ~621 | 2h | $5 |
| **TOTAL** | **95,086** | **~285,000** | **~48h** | **~$255** |

### Cost Breakdown

```
Claude Haiku 4.5 (OpenRouter):
  - Input: $0.25 / 1M tokens
  - Output: $1.25 / 1M tokens
  - Average: ~3,000 tokens per example (500 input + 2,500 output)
  - Total: ~285M tokens → $250

GPT-4o (Formulas only):
  - Input: $2.50 / 1M tokens
  - Output: $10.00 / 1M tokens
  - Total: 207 examples → $5

Total: $255
```

---

## 🛠️ Customization

### Add New Topics

Edit the topic list in each generator:

```python
# generator_chat_rag.py
TOPICS = {
    "Matematica": {
        "count": 1000,
        "seed_questions": [
            "Spiega il teorema di Pitagora",
            "Come si risolve un'equazione di secondo grado",
            # Add more...
        ]
    },
    # Add new topics...
}
```

### Adjust Concurrency

```python
# In generator script
MAX_CONCURRENT = 45  # Reduce if hitting rate limits
BATCH_DELAY_MS = 500  # Increase for more conservative rate limiting
```

### Change Model

```python
# openrouter_client.py
MODEL = "anthropic/claude-3.5-haiku"  # Current
# MODEL = "anthropic/claude-3.5-sonnet"  # More expensive, higher quality
# MODEL = "openai/gpt-4o"  # Alternative provider
```

---

## 📚 Documentation

- **[API_CONFIGURATIONS.md](docs/API_CONFIGURATIONS.md)** - Complete API settings and keys
- **[BATCH_CONCURRENCY.md](docs/BATCH_CONCURRENCY.md)** - Performance tuning guide
- **[DATASET_SPECIFICATIONS.md](docs/DATASET_SPECIFICATIONS.md)** - Format specifications

**Version-specific READMEs**:
- [v2.0_base/README.md](v2.0_base/README.md) - Base dataset (25K examples)
- [v2.1_medicina/README.md](v2.1_medicina/README.md) - Medical specialization (18K)
- [v2.2_scienze/README.md](v2.2_scienze/README.md) - Sciences (10K)
- [v2.3_logica/README.md](v2.3_logica/README.md) - Logic (10K)
- [v2.4_ingegneria/README.md](v2.4_ingegneria/README.md) - Engineering (8K)
- [v2.5_emotional_support/README.md](v2.5_emotional_support/README.md) - Emotional Intelligence (7K)
- [v2.6_tone_flexibility/README.md](v2.6_tone_flexibility/README.md) - Tone Adaptation (16K)
- [v2.7_humanities_softskills/README.md](v2.7_humanities_softskills/README.md) - Humanities (12K)
- [formulas/README.md](formulas/README.md) - LaTeX Formulas (207)

---

## 🎓 Citation

If you use this dataset or generation methodology, please cite:

```bibtex
@misc{qwen3-all1e-dataset-2025,
  title={Qwen3 Fine-tuning Dataset Generation for Italian Educational AI},
  author={ALL1E Team},
  year={2025},
  publisher={GitHub},
  howpublished={\url{https://github.com/onepixac/qwen3-dataset-generation}}
}
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- **Anthropic** - Claude Haiku 4.5 API (via OpenRouter)
- **OpenAI** - GPT-4o for formula generation
- **HuggingFace** - Qwen2.5-Math-7B inference
- **OpenRouter** - Unified API gateway

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/onepixac/qwen3-dataset-generation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/onepixac/qwen3-dataset-generation/discussions)
- **Email**: support@all1e.com

---

**Last Updated**: 2025-11-02 | **Version**: 1.0.0 | **Status**: Production
