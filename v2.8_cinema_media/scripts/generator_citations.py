#!/usr/bin/env python3
"""
Citations Generator for Cinema & Media Studies (v2.8)
Generates chat responses with proper source citations [1][2][3]
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

CITATIONS_TOPICS = {
    "linguaggio_cinematografico": 400,
    "storia_cinema": 400,
    "analisi_narrativa": 300,
    "generi": 300,
    "registi": 300,
    "sociologia": 200,
    "linguistica": 100
}

SYSTEM_PROMPT = """Sei ALL1E TUTOR, esperto in Cinema e Media Studies.
Genera coppie domanda-risposta dove la risposta include citazioni delle fonti usando il formato [1][2][3].

Le risposte devono:
- Essere pedagogicamente efficaci
- Includere citazioni numerate [1][2][3] per ogni affermazione
- Collegare concetti diversi
- Stimolare approfondimento"""

CITATIONS_PROMPT = """Genera UNA coppia domanda-risposta con citazioni su: {topic}

La risposta deve:
1. Rispondere in modo completo e pedagogico
2. Includere citazioni [1][2][3] dopo ogni affermazione
3. Fornire 2-3 fonti fittizie ma realistiche
4. Essere chiara e ben strutturata

Rispondi SOLO con JSON:
{{
    "question": "La domanda dello studente",
    "answer": "Risposta con citazioni [1][2][3]",
    "sources": [
        {{"title": "Titolo fonte 1", "author": "Autore", "year": 2020}},
        {{"title": "Titolo fonte 2", "author": "Autore", "year": 2019}}
    ]
}}"""


class CitationsGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        self.output_file = self.output_dir / "cinema_media_citations.jsonl"
        
    async def generate_citation_pair(self, topic: str) -> Dict:
        """Generate a single Q&A pair with citations"""
        prompt = CITATIONS_PROMPT.format(topic=topic)
        
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
            
            # Build sources text
            sources_text = "\n\nFonti:\n"
            for i, source in enumerate(data.get("sources", []), 1):
                sources_text += f"[{i}] {source['author']} ({source['year']}). {source['title']}\n"
            
            return {
                "messages": [
                    {
                        "role": "system",
                        "content": "Sei ALL1E TUTOR, assistente educativo per Cinema e Media Studies. Rispondi sempre citando le fonti con [1][2][3]."
                    },
                    {
                        "role": "user",
                        "content": data["question"]
                    },
                    {
                        "role": "assistant",
                        "content": data["answer"] + sources_text
                    }
                ],
                "metadata": {
                    "type": "citations",
                    "topic": topic,
                    "has_sources": True,
                    "num_sources": len(data.get("sources", [])),
                    "domain": "cinema_media_studies",
                    "version": "v2.8"
                }
            }
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response: {response}")
    
    async def generate_batch(self, topic: str, count: int) -> List[Dict]:
        """Generate a batch of citation pairs"""
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        async def generate_with_semaphore():
            async with semaphore:
                return await self.generate_citation_pair(topic)
        
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
        """Generate all citation pairs"""
        print("=" * 80)
        print("📚 CINEMA & MEDIA STUDIES - CITATIONS GENERATION (v2.8)")
        print("=" * 80)
        print()
        print(f"Total target: {sum(CITATIONS_TOPICS.values())} citation examples")
        print()
        
        all_pairs = []
        
        for topic, count in CITATIONS_TOPICS.items():
            print(f"📚 Generating {count} citation examples for: {topic}")
            pairs = await self.generate_batch(topic, count)
            all_pairs.extend(pairs)
            
            # Small delay between topics
            await asyncio.sleep(0.5)
        
        # Save to JSONL
        print()
        print(f"💾 Saving {len(all_pairs)} citation examples to: {self.output_file}")
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for pair in all_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + '\n')
        print("✅ Saved")
        
        # Statistics
        print()
        print("📊 Statistics:")
        print(f"  Generated: {len(all_pairs)}")
        print(f"  Failed: {sum(CITATIONS_TOPICS.values()) - len(all_pairs)}")
        print(f"  Success rate: {len(all_pairs)/sum(CITATIONS_TOPICS.values())*100:.1f}%")
        print()


async def main():
    generator = CitationsGenerator()
    await generator.generate_all()


if __name__ == "__main__":
    asyncio.run(main())
