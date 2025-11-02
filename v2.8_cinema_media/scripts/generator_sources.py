#!/usr/bin/env python3
"""
Sources Generator for Cinema & Media Studies (v2.8)
Generates chat with explicit source references and document IDs
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List
from tqdm.asyncio import tqdm
from dotenv import load_dotenv
from openrouter_client import OpenRouterClient

# Load environment variables
load_dotenv()

# Configuration
import os
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", 45))

SOURCES_TOPICS = {
    "linguaggio_cinematografico": 250,
    "storia_cinema": 250,
    "analisi_narrativa": 200,
    "generi": 200,
    "registi": 200,
    "sociologia": 150,
    "linguistica": 50
}

SYSTEM_PROMPT = """Sei ALL1E TUTOR, esperto in Cinema e Media Studies.
Genera coppie domanda-risposta che referenziano esplicitamente le fonti documentali.

Le risposte devono:
- Menzionare esplicitamente i documenti consultati
- Indicare capitoli, sezioni o pagine
- Essere pedagogicamente efficaci
- Dimostrare uso appropriato delle fonti"""

SOURCES_PROMPT = """Genera UNA coppia domanda-risposta con riferimenti alle fonti su: {topic}

La risposta deve:
1. Rispondere in modo completo
2. Menzionare fonti specifiche (es: "Come spiegato nel capitolo 3 di...")
3. Indicare dove trovare approfondimenti
4. Essere pedagogicamente efficace

Rispondi SOLO con JSON:
{{
    "question": "La domanda dello studente",
    "answer": "Risposta con riferimenti espliciti alle fonti",
    "source_references": [
        "Capitolo 3: Titolo",
        "Sezione 2.4: Titolo"
    ]
}}"""


class SourcesGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        self.output_file = self.output_dir / "cinema_media_sources.jsonl"
        
    async def generate_sources_pair(self, topic: str) -> Dict:
        """Generate a single Q&A pair with source references"""
        prompt = SOURCES_PROMPT.format(topic=topic)
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat_completion_with_retry(
            messages=messages,
            temperature=0.8,
            max_tokens=2048
        )
        
        # Parse JSON response
        try:
            data = json.loads(response)
            
            # Build source references text
            refs_text = "\n\nPuoi approfondire in:\n"
            for ref in data.get("source_references", []):
                refs_text += f"• {ref}\n"
            
            return {
                "messages": [
                    {
                        "role": "system",
                        "content": "Sei ALL1E TUTOR, assistente educativo per Cinema e Media Studies. Referenzia sempre le fonti documentali nei tuoi responsi."
                    },
                    {
                        "role": "user",
                        "content": data["question"]
                    },
                    {
                        "role": "assistant",
                        "content": data["answer"] + refs_text
                    }
                ],
                "metadata": {
                    "type": "sources",
                    "topic": topic,
                    "has_source_refs": True,
                    "num_refs": len(data.get("source_references", [])),
                    "domain": "cinema_media_studies",
                    "version": "v2.8"
                }
            }
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response: {response}")
    
    async def generate_batch(self, topic: str, count: int) -> List[Dict]:
        """Generate a batch of source reference pairs"""
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        async def generate_with_semaphore():
            async with semaphore:
                return await self.generate_sources_pair(topic)
        
        tasks = [generate_with_semaphore() for _ in range(count)]
        results = []
        
        with tqdm(total=count, desc=f"  {topic}", leave=True) as pbar:
            for coro in asyncio.as_completed(tasks):
                try:
                    result = await coro
                    results.append(result)
                except Exception as e:
                    print(f"\n⚠️  Error: {e}")
                finally:
                    pbar.update(1)
        
        return results
    
    async def generate_all(self):
        """Generate all source reference pairs"""
        print("=" * 80)
        print("📖 CINEMA & MEDIA STUDIES - SOURCES GENERATION (v2.8)")
        print("=" * 80)
        print()
        print(f"Total target: {sum(SOURCES_TOPICS.values())} source examples")
        print()
        
        all_pairs = []
        
        for topic, count in SOURCES_TOPICS.items():
            print(f"📖 Generating {count} source examples for: {topic}")
            pairs = await self.generate_batch(topic, count)
            all_pairs.extend(pairs)
            
            # Small delay between topics
            await asyncio.sleep(0.5)
        
        # Save to JSONL
        print()
        print(f"💾 Saving {len(all_pairs)} source examples to: {self.output_file}")
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for pair in all_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + '\n')
        print("✅ Saved")
        
        # Statistics
        print()
        print("📊 Statistics:")
        print(f"  Generated: {len(all_pairs)}")
        print(f"  Failed: {sum(SOURCES_TOPICS.values()) - len(all_pairs)}")
        print(f"  Success rate: {len(all_pairs)/sum(SOURCES_TOPICS.values())*100:.1f}%")
        print()


async def main():
    generator = SourcesGenerator()
    await generator.generate_all()


if __name__ == "__main__":
    asyncio.run(main())
