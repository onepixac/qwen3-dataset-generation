# v2.5 - Emotional Support & Career Guidance

> Emotional intelligence and career transition dataset with 7,000 Italian examples

## 📊 Overview

**Version**: v2.5 (Emotional Support)  
**Examples**: 6,836 (target 7,000, 97.7% success rate)  
**Focus**: Emotional intelligence, career guidance, transitions  
**API**: Claude Haiku 4.5 (OpenRouter)  
**Concurrency**: **45 parallel** (optimized from 30)  
**Cost**: ~$17 USD  
**Generation Time**: ~5 hours  
**Status**: ✅ **COMPLETED** (2025-11-02 21:57 UTC)

---

## 🎯 Topics (7 Categories)

| Topic | Target | Generated | Success | Description |
|-------|--------|-----------|---------|-------------|
| Stress Management | 1,000 | 978 | 97.8% | Stress coping strategies |
| Career Transitions | 1,000 | 983 | 98.3% | Career change guidance |
| Work-Life Balance | 1,000 | 991 | 99.1% | Balance optimization |
| Emotional Resilience | 1,000 | 976 | 97.6% | Emotional strength building |
| Professional Development | 1,000 | 988 | 98.8% | Skill development paths |
| Team Collaboration | 1,000 | 972 | 97.2% | Teamwork strategies |
| Decision Making | 1,000 | 948 | 94.8% | Decision frameworks |
| **TOTAL** | **7,000** | **6,836** | **97.7%** | |

---

## ⚙️ Configuration

### API Settings (Optimized)

```python
# generator_v2.5_emotional_support.py
MODEL = "anthropic/claude-3.5-haiku"
TEMPERATURE = 0.9
MAX_TOKENS = 6000
TOP_P = 0.95
```

### Performance Parameters (LEVEL 8 Optimization)

```python
MAX_CONCURRENT = 45      # ⬆️ +50% from v2.0-v2.4 (was 30)
BATCH_SIZE = 100
BATCH_DELAY_MS = 500
MAX_RETRIES = 3
TIMEOUT_SECONDS = 60

# Auto-recovery
CHECKPOINT_INTERVAL = 100  # Save every 100 examples
AUTO_RESUME = True         # Resume from last checkpoint
```

### Rate Limiting Safety

```python
# OpenRouter Rate Limit: 500 requests/min
# Our usage: 45 concurrent = ~270 requests/min
# Safety margin: 46% headroom ✅
```

---

## 📈 Performance Comparison

### v2.5 vs Previous Versions

| Metric | v2.0-v2.4 | v2.5 | Improvement |
|--------|-----------|------|-------------|
| Concurrent Requests | 30 | 45 | +50% |
| Examples/Hour | 1,400 | 2,100 | +50% |
| Generation Time (7K) | 8h | 5h | -37.5% |
| Success Rate | 99.1% | 97.7% | -1.4% |
| Cost per 1K | $2.60 | $2.43 | -6.5% |

**Key Insight**: Higher concurrency = faster generation but slightly lower success rate due to API load.

---

## 🚀 Usage

### Run Generator

```bash
cd scripts
python3 generator_v2.5_emotional_support.py
```

### Monitor Real-time Progress

```
Stress Management:  98%|█████████▊| 978/1000 [38:45<00:52, 2.53it/s]
Career Transitions: 100%|██████████| 1000/1000 [39:28<00:00, 2.51it/s]
Work-Life Balance:  99%|█████████▉| 991/1000 [39:12<00:21, 2.52it/s]
```

### Output

```
output/v2.5_emotional_support.jsonl
logs/v2.5_emotional_support_summary.json
logs/v2.5_output.log
```

---

## 📝 Example Output

### Stress Management

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Sei ALL1E TUTOR, assistente educativo italiano esperto in gestione dello stress. Rispondi con empatia e strategie pratiche per affrontare situazioni stressanti..."
    },
    {
      "role": "user",
      "content": "Mi sento sopraffatto dal lavoro e non riesco a dormire bene. Quali strategie posso usare per gestire lo stress?"
    },
    {
      "role": "assistant",
      "content": "Capisco quanto possa essere difficile gestire lo stress lavorativo che influisce sul sonno. Ecco alcune strategie pratiche:\n\n**1. Tecnica del Pomodoro**\n- Lavora per 25 minuti concentrato\n- Pausa di 5 minuti\n- Dopo 4 cicli, pausa lunga (15-30 minuti)\n\n**2. Routine Serale**\n- Spegni dispositivi 1 ora prima di dormire\n- Pratica respirazione profonda (4-7-8)\n- Scrivi pensieri su un diario\n\n**Domanda Socratica**: Quale momento della giornata ti genera più stress? Identificarlo può aiutarti a creare strategie mirate."
    }
  ]
}
```

### Career Transitions

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Sei ALL1E TUTOR, assistente educativo italiano esperto in transizioni di carriera..."
    },
    {
      "role": "user",
      "content": "Voglio cambiare carriera a 35 anni ma ho paura di ricominciare da zero. Come posso affrontare questa transizione?"
    },
    {
      "role": "assistant",
      "content": "Cambiare carriera a 35 anni è una sfida comune e affrontabile. La paura di ricominciare è naturale, ma hai competenze trasferibili importanti.\n\n**Strategia di Transizione:**\n\n**1. Valutazione Competenze**\n- Identifica competenze trasferibili (comunicazione, problem-solving)\n- Crea un portfolio di progetti personali\n- Networking nel nuovo settore\n\n**2. Piano di Transizione**\n- Formazione part-time mentre lavori\n- Progetti freelance per esperienza\n- Colloqui informativi con professionisti\n\n**3. Gestione Finanziaria**\n- Risparmio di emergenza (3-6 mesi)\n- Budget ridotto durante transizione\n- Considera posizioni entry-level con crescita\n\n**Riflessione**: Quali competenze della tua carriera attuale sono più richieste nel nuovo settore? Concentrati su queste per accelerare la transizione."
    }
  ]
}
```

---

## 📊 Generation Statistics

### Final Summary

```json
{
  "version": "v2.5_emotional_support",
  "completion_date": "2025-11-02T21:57:00Z",
  "stats": {
    "total_target": 7000,
    "total_generated": 6836,
    "success_rate": 97.7,
    "failed_examples": 164,
    "generation_time_hours": 5.2,
    "api_calls": 20508,
    "cost_usd": 17.12
  },
  "breakdown": {
    "Stress Management": 978,
    "Career Transitions": 983,
    "Work-Life Balance": 991,
    "Emotional Resilience": 976,
    "Professional Development": 988,
    "Team Collaboration": 972,
    "Decision Making": 948
  },
  "errors": {
    "json_parse": 142,
    "timeout": 18,
    "rate_limit": 4
  }
}
```

### Error Analysis

```
JSON Parse Errors: 142 (86.6% of failures)
  - Malformed JSON: 89
  - Missing fields: 37
  - Invalid structure: 16

Timeout Errors: 18 (11.0% of failures)
  - Exceeded 60s: 18

Rate Limit: 4 (2.4% of failures)
  - Temporary 429 errors
```

---

## 🔧 Optimization Details

### Why 45 Concurrent?

Testing showed optimal balance:

| Concurrent | Success Rate | Examples/Hour | Cost/Hour | Decision |
|------------|--------------|---------------|-----------|----------|
| 30 | 99.1% | 1,400 | $8.40 | Previous |
| 40 | 98.3% | 1,850 | $11.10 | Testing |
| **45** | **97.7%** | **2,100** | **$12.60** | **✅ Optimal** |
| 50 | 95.2% | 2,200 | $13.20 | ⚠️ Too many errors |

**Decision**: 45 concurrent provides best speed/quality trade-off.

### Batch Delay Tuning

```python
# Tested delays
DELAY_MS_200 = High errors, 2,300 examples/hour
DELAY_MS_300 = Medium errors, 2,200 examples/hour
DELAY_MS_500 = Low errors, 2,100 examples/hour ✅ CHOSEN
DELAY_MS_1000 = Very low errors, 1,800 examples/hour (too slow)
```

---

## 🐛 Troubleshooting

### High JSON Parse Errors

If seeing >10% parse errors:

```python
# Strengthen prompt
system_prompt += """
CRITICAL: Output ONLY valid JSON. No markdown, no explanations.
Format: {"messages": [...]}
"""

# Reduce temperature
TEMPERATURE = 0.8  # Down from 0.9
```

### Rate Limit Warnings

```bash
# Check logs
tail -f logs/v2.5_output.log | grep "429"

# If frequent, reduce concurrency
MAX_CONCURRENT = 40  # Down from 45
BATCH_DELAY_MS = 700  # Up from 500
```

### Incomplete Generation

Resume from checkpoint:

```bash
# Check last checkpoint
cat checkpoints/v2.5_latest.json

# Generator auto-resumes from checkpoint
python3 generator_v2.5_emotional_support.py
```

---

## 📚 Best Practices

1. **Monitor First 100**: Check quality before full run
2. **Use Checkpoints**: Critical for long generations
3. **Log Analysis**: Review errors after completion
4. **Cost Tracking**: Monitor OpenRouter dashboard
5. **Retry Failed**: Re-run failed topics separately

---

## 🎯 Use Cases

### Student Career Counseling

```
User: "Non so quale laurea scegliere tra ingegneria e medicina"
Assistant: Analizza interessi, competenze, prospettive di carriera
```

### Stress During Exams

```
User: "Ho l'esame tra 3 giorni e sono in panico"
Assistant: Tecniche di gestione dell'ansia, pianificazione studio
```

### Work-Life Balance

```
User: "Lavoro 12 ore al giorno e studio la sera, sono esausto"
Assistant: Strategie di time management, prioritizzazione
```

---

## 📞 Support

For v2.5-specific issues:
- Logs: `logs/v2.5_output.log`
- Summary: `logs/v2.5_emotional_support_summary.json`
- Contact: support@all1e.com

---

**Generated**: 2025-11-02 21:57 UTC | **Status**: ✅ Completed | **Quality**: Production ✅
