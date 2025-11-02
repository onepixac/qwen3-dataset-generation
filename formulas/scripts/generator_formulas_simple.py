"""
SIMPLE Formula Generator - NO CLASSIFICATION BOTTLENECK
- Takes first 2,100 valid formulas (no category balancing)
- 150 concurrent with retry logic
- Much faster sampling (no classification loop)
"""
import asyncio
import aiohttp
import json
from pathlib import Path
from tqdm.asyncio import tqdm as async_tqdm
from datasets import load_dataset

class FormulasSimpleGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_file = self.base_dir / "output" / "formulas_hf.jsonl"
        self.checkpoint_file = self.base_dir / "checkpoints" / "formulas_hf_checkpoint.json"
        self.output_file.parent.mkdir(exist_ok=True)
        self.checkpoint_file.parent.mkdir(exist_ok=True)
        
        self.api_key = "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"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "openai/gpt-4o-mini"
        
        # Config
        self.max_concurrent = 150
        self.max_retries = 3
        self.target_count = 2100
    
    def create_prompt(self, formula: str) -> str:
        """Create educational prompt"""
        return f"""Sei un esperto educativo italiano. Genera una conversazione educativa su questa formula:

Formula: {formula}

Genera SOLO JSON (no markdown):
{{
  "question": "Domanda naturale dello studente su questa formula (max 25 parole)",
  "answer": "Spiegazione completa con:
- [Breakdown]: componenti formula
- [Significato]: cosa rappresenta
- [Esempio pratico]: applicazione reale
- [Domande socratiche]: 2 domande per approfondire (tono incoraggiante)

Lunghezza: 200-350 parole, italiano pedagogico"
}}"""
    
    def parse_response(self, content: str) -> dict:
        """Extract JSON from API response"""
        try:
            # Remove markdown wrapper
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            content = content.strip()
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start != -1 and end > start:
                return json.loads(content[start:end])
        except:
            pass
        return {}
    
    def format_for_training(self, qa: dict, formula: str) -> dict:
        """Format as training example"""
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "Sei ALL1E TUTOR, esperto educativo in matematica, fisica e chimica. Spieghi formule con chiarezza e pedagogia."
                },
                {
                    "role": "user",
                    "content": qa['question']
                },
                {
                    "role": "assistant",
                    "content": qa['answer']
                }
            ],
            "metadata": {
                "type": "formula_explanation",
                "formula": formula,
                "source": "huggingface_80M"
            }
        }
    
    def load_checkpoint(self):
        """Load checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {"all_data": []}
    
    def save_checkpoint(self, all_data):
        """Save checkpoint"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump({"all_data": all_data}, f)
    
    async def generate_one_formula(self, formula: str, semaphore, session) -> dict:
        """Generate explanation with ROBUST retry (max 3 attempts)"""
        async with semaphore:
            for attempt in range(self.max_retries):
                try:
                    prompt = self.create_prompt(formula)
                    
                    async with session.post(
                        self.api_url,
                        json={
                            "model": self.model,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.7,
                            "max_tokens": 3000
                        },
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            content = data['choices'][0]['message']['content']
                            qa = self.parse_response(content)
                            
                            # Validate response
                            if 'question' in qa and 'answer' in qa and len(qa['answer']) > 150:
                                return self.format_for_training(qa, formula)
                        
                        # Retry on non-200 or invalid response
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(0.5 * (attempt + 1))
                        
                except asyncio.TimeoutError:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1)
                except Exception:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(0.5)
            
            return None
    
    async def generate_async(self):
        """Generate formulas with 150 concurrent + retry logic"""
        print(f"\n{'='*80}\n🔬 SIMPLE FORMULAS GENERATOR - NO CLASSIFICATION\n{'='*80}")
        print(f"   Strategy: Take first 2,100 valid formulas (no category filtering)")
        print(f"   Concurrent: {self.max_concurrent}")
        print(f"   Max retries per formula: {self.max_retries}")
        
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        all_data = checkpoint.get("all_data", [])
        
        if all_data:
            print(f"   ✅ Resuming from {len(all_data)} valid examples")
        
        # Load HuggingFace dataset
        print("\n📥 Loading HuggingFace dataset (streaming)...")
        ds = load_dataset('OleehyO/latex-formulas-80M', 'en', split='train', streaming=True)
        
        # Sample first 2,100 VALID formulas (length filter only)
        print(f"\n🔍 Sampling first {self.target_count} valid formulas...")
        
        formulas = []
        for sample in ds:
            latex = sample['latex_formula']
            # Simple filter: length between 10-500 characters
            if 10 <= len(latex) <= 500:
                formulas.append(latex)
            
            if len(formulas) >= self.target_count:
                break
            
            # Progress every 500 formulas
            if len(formulas) % 500 == 0:
                print(f"   Sampled {len(formulas)}/{self.target_count}...")
        
        print(f"\n✅ Sampled {len(formulas)} formulas")
        
        # Generate with retry until we reach target
        needed = self.target_count - len(all_data)
        print(f"\n📊 Need {needed} more valid examples (150 concurrent + retry)...")
        
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.generate_one_formula(formula, semaphore, session)
                for formula in formulas
            ]
            
            results = []
            for coro in async_tqdm(
                asyncio.as_completed(tasks),
                total=len(tasks),
                desc="  Generating"
            ):
                result = await coro
                if result:
                    results.append(result)
                
                # Checkpoint every 100 valid
                if len(results) % 100 == 0 and len(results) > 0:
                    temp_data = all_data + results
                    self.save_checkpoint(temp_data)
                    
                    # Save to file
                    with open(self.output_file, 'w', encoding='utf-8') as f:
                        for item in temp_data:
                            f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
            # Add all valid results
            all_data.extend(results)
        
        # Final save
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for item in all_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        self.save_checkpoint(all_data)
        
        print(f"\n✅ GENERATION COMPLETE: {len(all_data):,} valid examples")
        print(f"   Success rate: {len(results)/len(formulas)*100:.1f}%")
        
        return all_data

async def main():
    print("="*80 + "\n🔬 SIMPLE FORMULAS GENERATOR\n" + "="*80)
    generator = FormulasSimpleGenerator()
    await generator.generate_async()
    print("\n✅ ALL FORMULAS GENERATED SUCCESSFULLY")

if __name__ == "__main__":
    asyncio.run(main())
