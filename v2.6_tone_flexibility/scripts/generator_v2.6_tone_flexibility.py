"""
Generator for v2.6 Tone Flexibility Dataset
Target: 16,250 examples (Analogies, Colloquial, Friendly)
"""

import json
import argparse
import asyncio
from pathlib import Path
from typing import List, Dict
from tqdm.asyncio import tqdm
from openrouter_client import OpenRouterClient
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


class ToneFlexibilityGenerator:
    """Generate tone flexibility examples (analogies, slang, friendly)"""

    def __init__(self, topics_file: str, output_dir: str, log_dir: str):
        self.client = OpenRouterClient()
        self.topics_file = Path(topics_file)
        self.output_dir = Path(output_dir)
        self.log_dir = Path(log_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Load topics
        with open(self.topics_file, 'r', encoding='utf-8') as f:
            self.topics_config = json.load(f)

        self.dataset_name = self.topics_config['dataset_name']
        self.target_total = self.topics_config['target_total']
        self.topics = self.topics_config['topics']

    def create_prompt(self, topic: Dict) -> str:
        """Create generation prompt for specific topic"""
        topic_name = topic['name']
        description = topic['description']
        keywords = ', '.join(topic['keywords'])

        prompt = f"""Sei un esperto di educazione italiana specializzato in comunicazione flessibile e accessibile.

TOPIC: {topic_name}
DESCRIZIONE: {description}
KEYWORDS CHIAVE: {keywords}

OBIETTIVO: Genera ESATTAMENTE 12 conversazioni educative in italiano che dimostrino {topic_name.lower()}.

REQUISITI PER OGNI CONVERSAZIONE:
1. **Sistema**: Definisci ALL1E TUTOR con expertise in comunicazione educativa
2. **Domanda Studente**: Domanda naturale da studente italiano (usa keywords topic)
3. **Risposta Tutor**: 200-250 parole che:
   - Usa TONE SPECIFICO del topic ({topic_name})
   - Spiega concetto in modo chiaro e accessibile
   - Integra 2-3 domande socratiche
   - Esempio pratico relatable
   - Conclude con domanda follow-up

TONE GUIDELINES SPECIFICHE:
"""

        # Add topic-specific tone guidelines
        if "analogie" in topic_name.lower() or "analogia" in description.lower():
            prompt += """
- USA ANALOGIE CREATIVE: "Come se fosse...", "Immagina che...", "È tipo..."
- METAFORE QUOTIDIANE: Confronti con oggetti/situazioni familiari
- VISUALIZZAZIONE: Aiuta studente a "vedere" il concetto
- ENTUSIASMO: Mostra eccitazione per connessioni creative
"""
        elif "slang" in topic_name.lower() or "colloquial" in description.lower():
            prompt += """
- LINGUAGGIO COLLOQUIALE: "Tipo che", "Praticamente", "Letteralmente"
- ESPRESSIONI REGIONALI: Usa slang/espressioni del topic quando appropriato
- CONTRAZIONI INFORMALI: "Boh", "Vabbè", "Cioè"
- TONO CASUAL MA EDUCATIVO: Come parlare con amico, mantenendo precisione
"""
        elif "friendly" in topic_name.lower() or "amichevole" in description.lower():
            prompt += """
- TONO WARM & FRIENDLY: "Ehi!", "Ottima domanda!", "Ti capisco!"
- INCORAGGIAMENTO: "Dai che ce la fai!", "Sei sulla strada giusta!"
- EMPATIA: "È normale sentirsi così", "Succede a tutti"
- EMOJI APPROPRIATI: Usa 1-2 emoji per warmth (😊, 💪, 🎯, ✨)
"""
        else:
            prompt += """
- TONO ADATTIVO: Bilancia professionale e accessibile
- CHIAREZZA: Concetti complessi in linguaggio semplice
- COINVOLGIMENTO: Mantieni studente engaged e curioso
"""

        prompt += """

FORMATO OUTPUT: JSON array con 12 conversazioni in questo formato esatto:

```json
[
  {
    "messages": [
      {
        "role": "system",
        "content": "Sei ALL1E TUTOR, assistente educativo italiano esperto in [topic specifico]. [definisci expertise]"
      },
      {
        "role": "user",
        "content": "[Domanda studente - naturale, specifica, usa keywords topic]"
      },
      {
        "role": "assistant",
        "content": "[Risposta 200-250 parole con tone specifico del topic, analogie/slang/friendly tone, esempi pratici, 2-3 domande socratiche, conclude con follow-up]"
      }
    ]
  },
  ... [altre 11 conversazioni]
]
```

CRITICAL RULES:
✅ ESATTAMENTE 12 conversazioni diverse
✅ Ogni conversazione DEVE usare tone specifico del topic
✅ 200-250 parole per risposta assistant
✅ JSON valido, no commenti, no testo extra
✅ Italiano naturale e fluente
✅ Keywords topic integrate naturalmente

Genera ora le 12 conversazioni JSON:"""

        return prompt

    def generate_single_topic(self, topic: Dict, topic_idx: int) -> List[Dict]:
        """Generate examples for single topic (synchronous for ThreadPoolExecutor)"""
        topic_name = topic['name']
        target = topic['target_examples']

        print(f"\n🎯 Topic {topic_idx+1}/{len(self.topics)}: {topic_name} ({target} target)")

        results = []
        batch_size = 12  # Each prompt generates 12 conversations
        num_batches = (target + batch_size - 1) // batch_size

        with tqdm(total=target, desc=f"  {topic_name}", leave=False) as pbar:
            for batch_idx in range(num_batches):
                try:
                    prompt = self.create_prompt(topic)
                    conversations = self.client.generate_json(prompt, max_retries=3)

                    if conversations and isinstance(conversations, list):
                        # Validate structure
                        valid_conversations = []
                        for conv in conversations:
                            if isinstance(conv, dict) and "messages" in conv:
                                valid_conversations.append(conv)

                        results.extend(valid_conversations)
                        pbar.update(len(valid_conversations))

                        # Break if we reached target
                        if len(results) >= target:
                            break
                    else:
                        print(f"   ⚠️ Batch {batch_idx+1}: Invalid response format")

                except Exception as e:
                    print(f"   ❌ Batch {batch_idx+1} error: {e}")
                    continue

        print(f"  ✅ Generated {len(results)}/{target} for {topic_name}")
        return results[:target]  # Trim to exact target

    def generate_all_topics_parallel(self) -> Dict[str, List[Dict]]:
        """Generate all topics in parallel using ThreadPoolExecutor"""
        print(f"\n💬 {self.dataset_name.upper()} GENERATOR")
        print(f"   Target: {self.target_total} examples")
        print(f"   Topics: {len(self.topics)}")
        print(f"   Batch size: 12 conversations per API call")
        print(f"   Max concurrent: 15 workers\n")

        results_by_topic = {}

        # Process topics in parallel
        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_topic = {
                executor.submit(self.generate_single_topic, topic, idx): (topic, idx)
                for idx, topic in enumerate(self.topics)
            }

            for future in as_completed(future_to_topic):
                topic, idx = future_to_topic[future]
                try:
                    topic_results = future.result()
                    results_by_topic[topic['topic']] = topic_results
                except Exception as e:
                    print(f"   ❌ Topic {topic['name']} failed: {e}")
                    results_by_topic[topic['topic']] = []

        return results_by_topic

    def save_results(self, results_by_topic: Dict[str, List[Dict]]):
        """Save all results to output file"""
        output_file = self.output_dir / f"{self.dataset_name}.jsonl"

        total_saved = 0
        with open(output_file, 'w', encoding='utf-8') as f:
            for topic_key, conversations in results_by_topic.items():
                for conv in conversations:
                    f.write(json.dumps(conv, ensure_ascii=False) + '\n')
                    total_saved += 1

        print(f"\n✅ COMPLETED: {total_saved}/{self.target_total} examples")
        print(f"   Output: {output_file}\n")

        # Save summary
        summary_file = self.log_dir / f"{self.dataset_name}_summary.json"
        summary = {
            "dataset_name": self.dataset_name,
            "target_total": self.target_total,
            "generated_total": total_saved,
            "completion_rate": f"{(total_saved/self.target_total)*100:.1f}%",
            "timestamp": datetime.now().isoformat(),
            "topics": [
                {
                    "topic": topic['name'],
                    "target": topic['target_examples'],
                    "generated": len(results_by_topic.get(topic['topic'], [])),
                }
                for topic in self.topics
            ]
        }

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"📊 Summary: {summary_file}")

    def run(self):
        """Main execution"""
        results = self.generate_all_topics_parallel()
        self.save_results(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate v2.6 Tone Flexibility dataset")
    parser.add_argument(
        "--topics",
        default="topics/v2.6_tone_flexibility_topics.json",
        help="Path to topics JSON file"
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Output directory"
    )
    parser.add_argument(
        "--logs",
        default="logs",
        help="Logs directory"
    )

    args = parser.parse_args()

    generator = ToneFlexibilityGenerator(
        topics_file=args.topics,
        output_dir=args.output,
        log_dir=args.logs
    )

    generator.run()
