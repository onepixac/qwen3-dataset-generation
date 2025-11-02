"""
v2.8 Cinema & Media Studies - Cloze Test Generator
Using GPT-4o-mini via OpenRouter
"""

import asyncio
import json
import os
from tqdm.asyncio import tqdm
from openrouter_client import OpenRouterClient
from dotenv import load_dotenv

load_dotenv()

MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", 45))
BATCH_DELAY_MS = int(os.getenv("BATCH_DELAY_MS", 500))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 150))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

# Cloze topics (500 total)
CLOZE_TOPICS = {
    "terminologia_cinematografica": 200,  # inquadratura, montaggio, etc.
    "storia_cinema": 100,
    "registi_movimenti": 100,
    "sociologia_comunicazione": 50,
    "linguistica": 50
}

SYSTEM_PROMPT = """Sei ALL1E CLOZE GENERATOR specializzato in Cinema e Media Studies.

Genera esercizi fill-in-the-blank in italiano con terminologia tecnica.

Focus su:
- Terminologia cinematografica (inquadratura, montaggio, piano sequenza)
- Movimenti e correnti (neorealismo, nouvelle vague)
- Registi e opere
- Concetti di comunicazione
- Linguistica cognitiva

Output richiesto: JSON valido
{
  "messages": [
    {"role": "system", "content": "Sei ALL1E CLOZE GENERATOR..."},
    {"role": "user", "content": "[CHUNK: testo]"},
    {"role": "assistant", "content": "{\\\"sentence\\\": \\\"Il [BLANK] è una tecnica...\\\", \\\"correct_word\\\": \\\"montaggio\\\", \\\"explanation\\\": \\\"...\\\"}"}
  ]
}

Regole:
✅ [BLANK] nel punto giusto
✅ Parola corretta specifica
✅ Spiegazione educativa
✅ Termine tecnico importante"""

class ClozeGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self.generated_count = 0
        self.failed_count = 0
    
    async def generate_single(self, topic: str, index: int) -> dict:
        """Generate single cloze test"""
        async with self.semaphore:
            try:
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"[CHUNK: Contenuto su {topic}]\n\nGenera un cloze test tecnico"}
                ]
                
                response = await self.client.chat_completion_with_retry(
                    messages=messages,
                    max_retries=MAX_RETRIES,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                if not response:
                    return None
                
                try:
                    if "```json" in response:
                        response = response.split("```json")[1].split("```")[0].strip()
                    elif "```" in response:
                        response = response.split("```")[1].split("```")[0].strip()
                    
                    data = json.loads(response)
                    
                    if "messages" in data:
                        self.generated_count += 1
                        return data
                    else:
                        self.failed_count += 1
                        return None
                        
                except json.JSONDecodeError:
                    self.failed_count += 1
                    return None
                    
            except Exception:
                self.failed_count += 1
                return None
    
    async def generate_topic(self, topic: str, count: int) -> list:
        """Generate cloze tests for topic"""
        print(f"\n📝 Generating {count} cloze tests for: {topic}")
        
        tasks = [self.generate_single(topic, i) for i in range(count)]
        
        results = []
        for i in range(0, len(tasks), BATCH_SIZE):
            batch = tasks[i:i+BATCH_SIZE]
            batch_results = await tqdm.gather(*batch, desc=f"  {topic}")
            results.extend([r for r in batch_results if r is not None])
            
            if i + BATCH_SIZE < len(tasks):
                await asyncio.sleep(BATCH_DELAY_MS / 1000)
        
        return results
    
    async def generate_all(self) -> list:
        """Generate all cloze tests"""
        print("="*80)
        print("📝 CINEMA & MEDIA STUDIES - CLOZE GENERATION (v2.8)")
        print("="*80)
        print(f"\nTotal target: {sum(CLOZE_TOPICS.values())} cloze tests")
        
        all_results = []
        for topic, count in CLOZE_TOPICS.items():
            results = await self.generate_topic(topic, count)
            all_results.extend(results)
        
        return all_results
    
    def save_results(self, results: list, output_path: str):
        """Save to JSONL"""
        print(f"\n💾 Saving {len(results)} cloze tests to: {output_path}")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
        
        print(f"✅ Saved")
        print(f"\n📊 Statistics:")
        print(f"  Generated: {self.generated_count}")
        print(f"  Failed: {self.failed_count}")
        print(f"  Success rate: {(self.generated_count / (self.generated_count + self.failed_count) * 100):.1f}%")

async def main():
    generator = ClozeGenerator()
    results = await generator.generate_all()
    generator.save_results(results, "../output/cinema_media_cloze.jsonl")

if __name__ == "__main__":
    asyncio.run(main())
