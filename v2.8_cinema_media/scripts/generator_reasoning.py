#!/usr/bin/env python3
"""
Reasoning Question Generator for Cinema & Media Studies (v2.8)
Generates critical thinking questions with reasoning evaluation
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

REASONING_TOPICS = {
    "analisi_critica_film": 350,
    "teoria_cinema": 300,
    "interpretazione_opere": 300,
    "confronto_stili": 250,
    "evoluzione_linguaggio": 250,
    "impatto_culturale": 200,
    "semiotica_cinema": 150,
    "estetica_visiva": 150,
    "narratologia": 150,
    "linguistica_applicata": 100
}

SYSTEM_PROMPT = """Sei ALL1E TUTOR, esperto in Cinema e Media Studies.
Genera domande di ragionamento critico che richiedono analisi approfondita, confronto e sintesi.

Le domande devono:
- Richiedere pensiero critico e argomentazione
- Non avere una risposta univoca "giusta"
- Stimolare riflessione e connessioni
- Essere valutabili con criteri pedagogici

NON generare domande con risposta semplice o factual."""

REASONING_PROMPT = """Genera UNA domanda di ragionamento critico su: {topic}

La domanda deve:
1. Richiedere analisi approfondita e argomentazione
2. Connettere concetti diversi
3. Stimolare pensiero critico
4. Essere aperta ma valutabile

Rispondi SOLO con JSON:
{{
    "question": "La domanda di ragionamento",
    "reasoning_type": "analysis|comparison|synthesis|evaluation",
    "difficulty": "medium|hard",
    "expected_elements": ["elemento1", "elemento2", "elemento3"]
}}"""


class ReasoningGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        self.output_file = self.output_dir / "cinema_media_reasoning.jsonl"
        
    async def generate_reasoning_question(self, topic: str) -> Dict:
        """Generate a single reasoning question"""
        prompt = REASONING_PROMPT.format(topic=topic)
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat_completion_with_retry(
            messages=messages,
            temperature=0.8,
            max_tokens=1000
        )
        
        # Parse JSON response
        try:
            data = json.loads(response)
            return {
                "messages": [
                    {
                        "role": "system",
                        "content": "Sei ALL1E TUTOR, assistente educativo per Cinema e Media Studies. Valuta le risposte di ragionamento con feedback pedagogico costruttivo."
                    },
                    {
                        "role": "user",
                        "content": data["question"]
                    }
                ],
                "metadata": {
                    "type": "reasoning",
                    "topic": topic,
                    "reasoning_type": data.get("reasoning_type", "analysis"),
                    "difficulty": data.get("difficulty", "medium"),
                    "expected_elements": data.get("expected_elements", []),
                    "domain": "cinema_media_studies",
                    "version": "v2.8"
                }
            }
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response: {response}")
    
    async def generate_batch(self, topic: str, count: int) -> List[Dict]:
        """Generate a batch of reasoning questions"""
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        async def generate_with_semaphore():
            async with semaphore:
                return await self.generate_reasoning_question(topic)
        
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
        """Generate all reasoning questions"""
        print("=" * 80)
        print("📋 CINEMA & MEDIA STUDIES - REASONING GENERATION (v2.8)")
        print("=" * 80)
        print()
        print(f"Total target: {sum(REASONING_TOPICS.values())} reasoning questions")
        print()
        
        all_questions = []
        
        for topic, count in REASONING_TOPICS.items():
            print(f"📋 Generating {count} reasoning questions for: {topic}")
            questions = await self.generate_batch(topic, count)
            all_questions.extend(questions)
            
            # Small delay between topics
            await asyncio.sleep(0.5)
        
        # Save to JSONL
        print()
        print(f"💾 Saving {len(all_questions)} reasoning questions to: {self.output_file}")
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for question in all_questions:
                f.write(json.dumps(question, ensure_ascii=False) + '\n')
        print("✅ Saved")
        
        # Statistics
        print()
        print("📊 Statistics:")
        print(f"  Generated: {len(all_questions)}")
        print(f"  Failed: {sum(REASONING_TOPICS.values()) - len(all_questions)}")
        print(f"  Success rate: {len(all_questions)/sum(REASONING_TOPICS.values())*100:.1f}%")
        print()


async def main():
    generator = ReasoningGenerator()
    await generator.generate_all()


if __name__ == "__main__":
    asyncio.run(main())
