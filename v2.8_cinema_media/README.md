# v2.8 - Cinema & Media Studies

> Cinema, comunicazione e linguistica cognitiva dataset con GPT-4o-mini

## 📊 Overview

**Version**: v2.8 (Cinema & Media Studies)  
**Target Examples**: 10,000  
**Focus**: Cinema italiano/internazionale, comunicazione, linguistica  
**API**: **GPT-4o-mini** via OpenRouter (75% cheaper than Claude Haiku)  
**Concurrency**: 45 parallel  
**Status**: 🚀 **Ready for generation**  

---

## 🎬 Source Documents (7 books, 3,096 chunks)

| # | Titolo | Categoria | Chunks | Size |
|---|--------|-----------|--------|------|
| 1 | Storia del cinema (Thompson & Bordwell) | Cinema | ~1,283 | 2.5 MB |
| 2 | Cinema italiano 1905-2023 (Brunetta) | Cinema | ~784 | 1.5 MB |
| 3 | Manuale del film (Rondolino) | Cinema | ~487 | 975 KB |
| 4 | Metafora e vita quotidiana (Lakoff & Johnson) | Linguistica | ~282 | 565 KB |
| 5 | Il cinema italiano (Costa) | Cinema | ~145 | 290 KB |
| 6 | Teorie comunicazioni di massa | Sociologia | ~73 | 146 KB |
| 7 | Sociologia Comunicazione digitale | Sociologia | ~42 | 84 KB |

**Total**: 3,096 chunks → 10,000 examples target

---

## 🎯 Dataset Breakdown

### Chat/RAG (2,000 examples)

| Topic | Count | Focus |
|-------|-------|-------|
| Linguaggio cinematografico | 400 | Inquadrature, montaggio, colore |
| Storia del cinema | 400 | Neorealismo, nouvelle vague |
| Analisi narrativa | 300 | Struttura, personaggi, temi |
| Generi cinematografici | 300 | Noir, western, thriller |
| Registi e autori | 300 | Fellini, Rossellini, Visconti |
| Sociologia comunicazione | 200 | Teorie, media effects |
| Linguistica cognitiva | 100 | Metafore, semantica |

### Quiz (1,500 examples)

Same topic distribution as Chat

### Citations (800 examples)

Focus on film analysis with historical sources

### Cloze (500 examples)

Technical terminology (inquadrature, montaggio, etc.)

### Reasoning (200 examples)

Film criticism and analysis evaluation

---

## ⚙️ Configuration

### API Settings (GPT-4o-mini)

```python
MODEL = "openai/gpt-4o-mini"
TEMPERATURE = 0.9
MAX_TOKENS = 6000
TOP_P = 0.95
```

### Performance (Optimized)

```python
MAX_CONCURRENT = 45      # Parallel requests
BATCH_SIZE = 150         # Examples per batch
BATCH_DELAY_MS = 500     # Rate limiting
MAX_RETRIES = 3          # Retry failed requests
```

### Cost (GPT-4o-mini)

```
Input: $0.15 per 1M tokens
Output: $0.60 per 1M tokens
Average: ~$0.75 per 1M tokens

10,000 examples × 3,000 tokens average = 30M tokens
Estimated cost: ~$22 USD (vs $70 with Claude Haiku)

Savings: 68% cheaper! 🎉
```

---

## 🚀 Usage

### 1. Setup Environment

```bash
cd v2.8_cinema_media/scripts
pip install openai python-dotenv tqdm aiohttp
```

### 2. Configure API Key

Edit `.env` file:
```bash
OPENROUTER_API_KEY=your-key-here
MODEL=openai/gpt-4o-mini
MAX_CONCURRENT=45
```

### 3. Run Generators

```bash
# Chat/RAG
python3 generator_chat.py

# Quiz
python3 generator_quiz.py

# All generators
chmod +x run_all_generators.sh
./run_all_generators.sh
```

---

## 📈 Expected Performance

| Metric | Value |
|--------|-------|
| Total examples | 10,000 |
| API calls | ~30,000 (3x per example) |
| Time | ~8-12 hours |
| Cost | ~$22 USD |
| Success rate | 99%+ |

---

## 🎓 Educational Value

### New Domain Coverage

✅ **Cinema Studies** (not covered in v2.0-v2.7):
- Film history (Italian + International)
- Film language (shots, editing, color)
- Narrative analysis
- Directors and auteurs
- Film genres

✅ **Media Studies**:
- Mass communication theories
- Digital sociology
- Media effects

✅ **Cognitive Linguistics**:
- Conceptual metaphors (Lakoff & Johnson)
- Cognitive semantics

---

## 📝 Example Outputs

### Chat Example

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Sei ALL1E TUTOR, esperto in Cinema e Media Studies..."
    },
    {
      "role": "user",
      "content": "Spiega cos'è il neorealismo italiano"
    },
    {
      "role": "assistant",
      "content": "Il neorealismo italiano è un movimento cinematografico nato nel dopoguerra (1945-1952)...\n\n**Caratteristiche principali:**\n- Riprese in esterni reali\n- Attori non professionisti\n- Temi sociali\n\n**Film emblematici:**\n- Roma città aperta (Rossellini, 1945)\n- Ladri di biciclette (De Sica, 1948)\n\n**Domanda socratica**: Perché il neorealismo ha scelto di raccontare storie di persone comuni?"
    }
  ]
}
```

### Quiz Example

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Sei ALL1E QUIZ GENERATOR..."
    },
    {
      "role": "user",
      "content": "[CHUNK: Il montaggio cinematografico...]"
    },
    {
      "role": "assistant",
      "content": "{\"question\": \"Qual è la funzione principale del montaggio parallelo?\", \"options\": [\"Creare suspense alternando due azioni simultanee\", \"Ridurre la durata del film\", \"Migliorare l'audio\", \"Aggiungere effetti speciali\", \"Correggere gli errori di ripresa\"], \"correct_answer\": 0}"
    }
  ]
}
```

---

## 🔧 Scripts

### Core Scripts

- `openrouter_client.py` - OpenRouter API client (GPT-4o-mini)
- `generator_chat.py` - Chat/RAG generation
- `generator_quiz.py` - Quiz generation
- `generator_citations.py` - Citations with sources
- `generator_cloze.py` - Fill-in-the-blank
- `generator_reasoning.py` - Film criticism evaluation

### Utilities

- `extract_cinema_media_docs.py` - Extract from database
- `run_all_generators.sh` - Launch all generators
- `.env` - Configuration (API keys)

---

## 📊 Quality Metrics

Expected validation results:

```json
{
  "total_generated": 10000,
  "valid_json": 9900,
  "validation_rate": 99.0,
  "avg_response_length": 2800,
  "topic_coverage": {
    "cinema": 70,
    "sociologia": 20,
    "linguistica": 10
  }
}
```

---

## 🎯 Why GPT-4o-mini?

### Advantages

✅ **Cost**: 75% cheaper than Claude Haiku ($0.75/1M vs $3.00/1M)  
✅ **Speed**: Similar latency (~2-3s per response)  
✅ **Quality**: Excellent for Italian educational content  
✅ **JSON**: Reliable structured output  
✅ **Context**: 128K tokens window  

### Comparison

| Metric | Claude Haiku 4.5 | GPT-4o-mini | Savings |
|--------|------------------|-------------|---------|
| Input cost/1M | $0.25 | $0.15 | 40% |
| Output cost/1M | $1.25 | $0.60 | 52% |
| 10K examples | ~$70 | ~$22 | **68%** |

---

## 📞 Support

For v2.8-specific issues:
- Check `.env` configuration
- Review OpenRouter API key
- Monitor rate limits (500 req/min)
- Contact: support@all1e.com

---

**Generated**: 2025-11-02 | **Status**: Ready | **Model**: GPT-4o-mini 🚀
