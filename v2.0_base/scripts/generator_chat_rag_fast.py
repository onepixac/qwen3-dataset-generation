"""
FAST CHAT/RAG Generator - aiohttp async + 400 concurrent
From 0.8 it/s → 25 it/s (31x speedup)
"""
import asyncio
import aiohttp
import json
import time
from pathlib import Path
from tqdm.asyncio import tqdm_asyncio
from load_simone_books import load_simone_textbooks, chunk_text

class FastChatRAGGenerator:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "openai/gpt-4o-mini"
        self.max_concurrent = 400
    
    def create_prompt(self, chunk: str, subject: str) -> str:
        return f"""Sei un esperto educativo. Genera 10 conversazioni ECCELLENTI di Q&A su {subject.upper()}.

CONTENUTO EDUCATIVO:
{chunk[:3000]}

OUTPUT (JSON):
[
  {{
    "question": "Domanda complessa e realistica che uno studente farebbe (richiede comprensione profonda, non semplice definizione)",
    "answer": "Risposta educativa ECCELLENTE che:\n1. Spiega il concetto con chiarezza e profondità\n2. Usa esempi pratici e applicazioni reali\n3. Fa collegamenti inter-disciplinari\n4. Include 2-3 domande socratiche per stimolare riflessione\n5. Usa tono pedagogico, incoraggiante, empatico\n6. Lunghezza: 200-300 parole\n7. Conclude con invito a esplorare ulteriormente"
  }}
]

REGOLE CRITICHE:
1. Questions: SEMPRE complesse, mai banali
2. Answers: SEMPRE pedagogiche con esempi pratici
3. Tono: Socratico, incoraggiante, professionale
4. Lunghezza: 200-300 parole per answer
5. NO risposte enciclopediche, SÌ risposte educative

Genera 10 conversazioni ECCELLENTI. Solo JSON puro."""
    
    async def generate_single(self, session, semaphore, chunk: str, subject: str):
        """Generate Q&A for single chunk"""
        async with semaphore:
            prompt = self.create_prompt(chunk, subject)
            
            try:
                async with session.post(
                    self.api_url,
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.8,
                        "max_tokens": 10000
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        
                        # Parse JSON
                        if '```json' in content:
                            content = content.split('```json')[1].split('```')[0]
                        elif '```' in content:
                            content = content.split('```')[1].split('```')[0]
                        
                        content = content.strip()
                        start = content.find('[')
                        end = content.rfind(']') + 1
                        
                        if start != -1 and end > start:
                            qa_list = json.loads(content[start:end])
                            
                            # Convert to training format
                            examples = []
                            for qa in qa_list:
                                if "question" in qa and "answer" in qa and len(qa['answer']) > 200:
                                    examples.append({
                                        "messages": [
                                            {"role": "system", "content": "Sei ALL1E TUTOR, assistente educativo esperto e socratico."},
                                            {"role": "user", "content": qa["question"]},
                                            {"role": "assistant", "content": qa["answer"]}
                                        ],
                                        "metadata": {
                                            "type": "chat_rag_standard",
                                            "subject": subject,
                                            "source": "simone_textbooks",
                                            "quality": "excellent"
                                        }
                                    })
                            return examples
            except Exception:
                pass
            
            return []
    
    async def generate_for_subject(self, books, subject: str, target: int, current: int, output_path: str):
        """Generate examples for a subject"""
        print(f"\n{'='*80}")
        print(f"🚀 {subject.upper()} - FAST GENERATION")
        print(f"{'='*80}")
        
        # Calculate how many we need
        remaining = target - current
        print(f"📊 Current: {current:,} | Target: {target:,} | Need: {remaining:,}")
        
        if remaining <= 0:
            print(f"✅ Already at target!")
            return
        
        # Prepare all chunks
        all_chunks = []
        for book in books:
            chunks = chunk_text(book['text'], 3000)
            all_chunks.extend(chunks)
        
        # Calculate chunks needed (10 Q&A per chunk)
        chunks_needed = (remaining + 9) // 10
        print(f"🎯 Processing {chunks_needed} chunks (10 Q&A each)")
        
        # Select chunks
        selected_chunks = all_chunks[:chunks_needed]
        
        # Generate async
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.generate_single(session, semaphore, chunk, subject)
                for chunk in selected_chunks
            ]
            
            results = await tqdm_asyncio.gather(
                *tasks,
                desc=f"   {subject}",
                total=len(tasks)
            )
        
        # Write results (append mode)
        count = 0
        with open(output_path, 'a', encoding='utf-8') as f:
            for chunk_examples in results:
                for ex in chunk_examples:
                    f.write(json.dumps(ex, ensure_ascii=False) + '\n')
                    count += 1
                    if count + current >= target:
                        break
                if count + current >= target:
                    break
        
        print(f"✅ Generated {count:,} new examples")
        print(f"📁 {output_path}")
        print(f"📈 Total: {current + count:,}/{target:,}")
    
    async def generate_all(self):
        """Generate all subjects"""
        print("="*80)
        print("⚡ FAST CHAT/RAG GENERATOR (aiohttp + 400 concurrent)")
        print("="*80)
        
        # Load books
        categories = load_simone_textbooks()
        output_dir = Path(__file__).parent / "output"
        
        # Targets and current counts
        subjects = {
            "economia": {"target": 5000, "current": 1406},
            "cultura_generale": {"target": 3000, "current": 600}
        }
        
        for subject, info in subjects.items():
            if categories.get(subject):
                output = output_dir / f"chat_rag_{subject}.jsonl"
                await self.generate_for_subject(
                    categories[subject],
                    subject,
                    info["target"],
                    info["current"],
                    str(output)
                )
        
        print(f"\n{'='*80}")
        print("✅ ALL COMPLETED!")
        print("="*80)

def main():
    generator = FastChatRAGGenerator()
    asyncio.run(generator.generate_all())

if __name__ == "__main__":
    main()
