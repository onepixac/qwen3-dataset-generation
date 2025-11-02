"""
v2.8 Cinema & Media Studies - Quiz Generator
Using GPT-4o-mini via OpenRouter
"""

import asyncio
import json
import os
from datetime import datetime
from tqdm.asyncio import tqdm
from openrouter_client import OpenRouterClient
from dotenv import load_dotenv

load_dotenv()

MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", 45))
BATCH_DELAY_MS = int(os.getenv("BATCH_DELAY_MS", 500))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 150))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

# Quiz topics (1500 total)
QUIZ_TOPICS = {
    "linguaggio_cinematografico": 300,
    "storia_cinema": 300,
    "analisi_narrativa": 250,
    "generi_cinematografici": 250,
    "registi_autori": 250,
    "sociologia_comunicazione": 100,
    "linguistica_cognitiva": 50
}

SYSTEM_PROMPT = """Sei ALL1E QUIZ GENERATOR specializzato in Cinema e Media Studies.

Genera quiz educativi in italiano con 5 opzioni (numerate 1-5).

Topic supportati:
- Linguaggio cinematografico (inquadrature, montaggio, colore)
- Storia del cinema (neorealismo, nouvelle vague, etc.)
- Analisi narrativa (struttura, personaggi, temi)
- Generi cinematografici (noir, western, thriller)
- Registi e autori (Fellini, Rossellini, Visconti)
- Sociologia comunicazione
- Linguistica cognitiva

Output richiesto: JSON valido
{
  "messages": [
    {"role": "system", "content": "Sei ALL1E QUIZ GENERATOR..."},
    {"role": "user", "content": "[CHUNK: testo educativo]"},
    {"role": "assistant", "content": "{\\\"question\\\": \\\"...\\\", \\\"options\\\": [...], \\\"correct_answer\\\": 0-4}"}
  ]
}

Regole:
✅ Domanda chiara e specifica
✅ 5 opzioni plausibili
✅ correct_answer: indice 0-4
✅ Quiz basato su contenuto chunk
✅ Distractors realistici"""

class QuizGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self.generated_count = 0
        self.failed_count = 0
    
    async def generate_single(self, topic: str, index: int) -> dict:
        """Generate single quiz"""
        async with self.semaphore:
            try:
                # Simulate chunk content
                chunk_content = f"[Contenuto educativo su {topic} - esempio {index}]"
                
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"[CHUNK: {chunk_content}]\n\nGenera un quiz su: {topic}"}
                ]
                
                response = await self.client.chat_completion_with_retry(
                    messages=messages,
                    max_retries=MAX_RETRIES,
                    temperature=0.8  # Slightly lower for quiz consistency
                )
                
                if not response:
                    return None
                
                # Parse JSON
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
        """Generate quizzes for topic"""
        print(f"\n📝 Generating {count} quizzes for: {topic}")
        
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
        """Generate all quizzes"""
        print("="*80)
        print("📝 CINEMA & MEDIA STUDIES - QUIZ GENERATION (v2.8)")
        print("="*80)
        print(f"\nTotal target: {sum(QUIZ_TOPICS.values())} quizzes")
        
        all_results = []
        for topic, count in QUIZ_TOPICS.items():
            results = await self.generate_topic(topic, count)
            all_results.extend(results)
        
        return all_results
    
    def save_results(self, results: list, output_path: str):
        """Save to JSONL"""
        print(f"\n💾 Saving {len(results)} quizzes to: {output_path}")
        
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
    generator = QuizGenerator()
    results = await generator.generate_all()
    generator.save_results(results, "../output/cinema_media_quiz.jsonl")

if __name__ == "__main__":
    asyncio.run(main())
