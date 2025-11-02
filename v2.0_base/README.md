# v2.0 - Base Dataset

> Foundation dataset with 25,000 Italian educational examples across 6 task types

## 📊 Overview

**Version**: v2.0 (Base)  
**Examples**: 25,000  
**Task Types**: 6 (Chat/RAG, Quiz, Citations, Cloze, Reasoning, Function Calling)  
**API**: Claude Haiku 4.5 (OpenRouter)  
**Cost**: ~$65 USD  
**Generation Time**: ~18 hours  

---

## 🎯 Task Distribution

| Task Type | Examples | Script | Purpose |
|-----------|----------|--------|---------|
| Chat/RAG | 10,000 | `generator_chat_rag.py` | Q&A with document context |
| Quiz | 6,000 | `generator_quiz_correct.py` | Multiple choice questions |
| Citations | 4,000 | `generator_citations.py` | Responses with sources [1][2] |
| Cloze | 3,000 | `generator_cloze.py` | Fill-in-the-blank exercises |
| Reasoning | 2,000 | `generator_reasoning.py` | Critical thinking questions |
| Function Calling | 1,000 | `generator_function_calling.py` | Tool invocation (plotting) |

---

## ⚙️ Configuration

### API Settings

```python
# openrouter_client.py
MODEL = "anthropic/claude-3.5-haiku"
TEMPERATURE = 0.9  # High creativity
MAX_TOKENS = 6000  # Long responses
TOP_P = 0.95       # Diverse sampling
```

### Performance Parameters

```python
# All generators
MAX_CONCURRENT = 30      # Parallel API requests
BATCH_SIZE = 100         # Examples per batch
BATCH_DELAY_MS = 500     # Rate limiting delay
MAX_RETRIES = 3          # Retry failed requests
TIMEOUT_SECONDS = 60     # Request timeout
```

### Topics

```python
TOPICS = {
    "Matematica": 3000,
    "Fisica": 2500,
    "Chimica": 2000,
    "Biologia": 2000,
    "Storia": 2000,
    "Letteratura": 2000,
    "Filosofia": 1500,
    "Economia": 1500,
    "Informatica": 1500,
    "Ingegneria": 1500,
    "Medicina": 1500,
    "Diritto": 1000,
    "Geografia": 1000,
    "Arte": 1000,
    "Musica": 1000,
    "Lingue": 1000
}
```

---

## 🚀 Usage

### Run Single Generator

```bash
cd scripts
python3 generator_chat_rag.py
```

### Run All Generators (Parallel)

```bash
cd scripts
python3 master_generator.py
```

### Monitor Progress

Generators output real-time progress:

```
Matematica:  67%|███████▋   | 2010/3000 [12:34<06:11, 2.66it/s]
Fisica:      82%|█████████▏ | 2050/2500 [10:11<02:14, 3.35it/s]
Chimica:     45%|█████      | 900/2000 [04:30<05:30, 3.33it/s]
```

### Output Format

```
output/
├── chat_rag_cultura_generale.jsonl
├── quiz_matematica.jsonl
├── citations_biologia.jsonl
├── cloze_chimica.jsonl
├── reasoning_filosofia.jsonl
└── function_calling_matematica.jsonl
```

---

## 📝 Example Outputs

### Chat/RAG

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Sei ALL1E TUTOR, assistente educativo italiano esperto in matematica..."
    },
    {
      "role": "user",
      "content": "Spiega il teorema di Pitagora con esempi pratici"
    },
    {
      "role": "assistant",
      "content": "Il teorema di Pitagora stabilisce che in un triangolo rettangolo...\n\n**Esempio Pratico:**\nImmagina una scala lunga 5 metri appoggiata a un muro..."
    }
  ]
}
```

### Quiz

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Sei ALL1E QUIZ GENERATOR. Genera quiz educativi basati sui chunk..."
    },
    {
      "role": "user",
      "content": "[CHUNK: La fotosintesi clorofilliana è il processo...]"
    },
    {
      "role": "assistant",
      "content": "{\n  \"question\": \"Quale organulo cellulare è responsabile della fotosintesi?\",\n  \"options\": [\n    \"Mitocondrio\",\n    \"Cloroplasto\",\n    \"Ribosoma\",\n    \"Nucleo\",\n    \"Reticolo endoplasmatico\"\n  ],\n  \"correct_answer\": 2\n}"
    }
  ]
}
```

### Function Calling

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Sei ALL1E TUTOR con capacità di generare grafici matematici..."
    },
    {
      "role": "user",
      "content": "Mostrami il grafico della funzione y = sin(x) nell'intervallo [-2π, 2π]"
    },
    {
      "role": "assistant",
      "content": "Ecco il grafico della funzione seno:",
      "tool_calls": [
        {
          "type": "function",
          "function": {
            "name": "plotting_tool",
            "arguments": "{\"function\": \"sin(x)\", \"x_range\": [-6.28, 6.28], \"title\": \"Funzione Seno\"}"
          }
        }
      ]
    }
  ]
}
```

---

## 📈 Performance

### Generation Stats

```
Total Examples: 25,000
API Calls: ~75,000 (3 calls per example average)
Success Rate: 99.1%
Failed Examples: 225 (JSON validation errors)
Generation Time: 17h 43m
```

### Cost Breakdown

```
Input Tokens: ~12.5M tokens
Output Tokens: ~62.5M tokens
Total Cost: $65.47 USD

Breakdown:
  - Input: 12.5M × $0.25/1M = $3.13
  - Output: 62.5M × $1.25/1M = $78.13
  - Total: $81.26 (OpenRouter discount: ~$65)
```

### Concurrency Performance

| Concurrent Requests | Examples/Hour | Cost/Hour | Status |
|---------------------|---------------|-----------|--------|
| 10 | 600 | $3.60 | ⚠️ Too slow |
| 20 | 1,100 | $6.60 | ✅ Optimal |
| 30 | 1,400 | $8.40 | ✅ Current |
| 40 | 1,550 | $9.30 | ⚠️ Rate limit risk |

---

## 🔧 Customization

### Add New Topic

1. Edit generator script:

```python
TOPICS = {
    # Existing topics...
    "Astronomia": 1000,  # New topic
}
```

2. Add seed questions:

```python
SEED_QUESTIONS = {
    "Astronomia": [
        "Spiega la formazione delle stelle",
        "Qual è la differenza tra pianeta e stella?",
        "Come funziona un buco nero?",
    ]
}
```

3. Run generator:

```bash
python3 generator_chat_rag.py
```

### Adjust Quality vs Speed

```python
# Higher quality (slower, more expensive)
TEMPERATURE = 0.7        # More focused
MAX_CONCURRENT = 20      # Less parallel
MAX_TOKENS = 8000        # Longer responses

# Higher speed (lower quality)
TEMPERATURE = 0.95       # More diverse
MAX_CONCURRENT = 40      # More parallel
MAX_TOKENS = 4000        # Shorter responses
```

---

## 🐛 Troubleshooting

### Rate Limit Errors

```python
# Reduce concurrency
MAX_CONCURRENT = 20  # Down from 30

# Increase delays
BATCH_DELAY_MS = 1000  # Up from 500ms
```

### JSON Validation Failures

Check logs for common issues:

```bash
tail -f logs/chat_rag_*.log | grep "JSON parse error"
```

Common fixes:
- Adjust prompt to enforce JSON structure
- Increase `MAX_TOKENS` for longer responses
- Add JSON schema validation in prompt

### Memory Issues

```python
# Process in smaller batches
BATCH_SIZE = 50  # Down from 100

# Clear cache periodically
import gc
gc.collect()
```

---

## 📚 Scripts Reference

### generator_chat_rag.py

**Purpose**: Generate conversational Q&A with document context

**Key Features**:
- Socratic questioning
- Pedagogical explanations
- Multi-turn conversations
- Context-aware responses

**Prompt Template**:
```python
system_prompt = """Sei ALL1E TUTOR, assistente educativo italiano.
Rispondi con spiegazioni chiare e pedagogicamente efficaci.
Usa esempi pratici e domande socratiche per stimolare il pensiero critico."""
```

### generator_quiz_correct.py

**Purpose**: Generate multiple choice quizzes with 5 options

**Key Features**:
- 5 numbered options (1-5)
- Correct answer index (0-4)
- Distractor generation
- Explanation for each option

**Output Schema**:
```json
{
  "question": "string",
  "options": ["string", "string", "string", "string", "string"],
  "correct_answer": 0-4
}
```

### generator_citations.py

**Purpose**: Generate responses with source citations [1][2][3]

**Key Features**:
- In-text citations
- Source list at end
- Chunk-based retrieval
- RAG-style responses

**Citation Format**:
```
I sintomi principali sono [1]:
- Febbre alta [1][2]
- Mal di gola [2][3]

Fonti:
[1] Chunk 1 - Sintomi influenza
[2] Chunk 2 - Diagnosi
[3] Chunk 3 - Trattamento
```

---

## 📊 Quality Metrics

### Validation Results

```json
{
  "total_generated": 25000,
  "valid_json": 24775,
  "validation_rate": 99.1,
  "avg_response_length": 2547,
  "avg_generation_time": 2.1,
  "quality_checks": {
    "has_system_message": 100.0,
    "has_user_message": 100.0,
    "has_assistant_message": 99.9,
    "proper_role_alternation": 99.8,
    "italian_language": 99.7
  }
}
```

---

## 🎓 Best Practices

1. **Start Small**: Test with 100 examples before full generation
2. **Monitor Costs**: Track API usage in real-time
3. **Validate Early**: Check first 10 outputs for quality
4. **Use Checkpoints**: Enable auto-save every 100 examples
5. **Log Everything**: Keep detailed logs for debugging

---

## 📞 Support

For issues specific to v2.0:
- Check logs in `output/logs/`
- Review validation reports
- Contact: support@all1e.com

---

**Generated**: 2025-10-28 | **Status**: Production | **Quality**: Validated ✅
