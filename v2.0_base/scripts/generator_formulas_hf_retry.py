"""
OPTIMIZED Formula Generator - 150 concurrent + robust retry
- 150 concurrent requests (optimal balance)
- Max 3 retries per formula
- Samples exactly 2,100 formulas (no waste)
- Continues until 2,100 VALID examples generated
"""
import asyncio
import aiohttp
import json
from pathlib import Path
from tqdm.asyncio import tqdm as async_tqdm
from datasets import load_dataset
import random

class FormulasHFGeneratorRetry:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_file = self.base_dir / "output" / "formulas_hf.jsonl"
        self.checkpoint_file = self.base_dir / "checkpoints" / "formulas_hf_checkpoint.json"
        self.output_file.parent.mkdir(exist_ok=True)
        self.checkpoint_file.parent.mkdir(exist_ok=True)
        
        self.api_key = "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"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "openai/gpt-4o-mini"
        
        # OPTIMAL: 150 concurrent with retry
        self.max_concurrent = 150
        self.max_retries = 3
        
        # Target valid examples
        self.target_count = 2100
        self.targets = {
            "chemistry": 840,
            "physics": 630,
            "mathematics": 630
        }
    
    def classify_formula(self, latex: str) -> str:
        """Classify formula by domain"""
        latex_lower = latex.lower()
        # Chemistry indicators
        if any(x in latex_lower for x in ['\\ce{', 'mol', 'h_2o', 'co_2', 'reaction', 'equilibrium', 'chem']):
            return "chemistry"
        # Physics indicators
        elif any(x in latex_lower for x in ['velocity', 'force', 'energy', 'momentum', 'acceleration', '\\vec{', 'omega', 'phys']):
            return "physics"
        # Default to mathematics
        else:
            return "mathematics"
    
    def create_prompt(self, formula: str, formula_type: str) -> str:
        """Create educational prompt"""
        return f"""Sei un esperto educativo italiano. Genera una conversazione educativa su questa formula {formula_type}:

Formula: {formula}

Genera SOLO JSON (no markdown):
{{
  "question": "Domanda naturale dello studente su questa formula (max 25 parole)",
  "answer": "Spiegazione completa con:
- [Breakdown]: componenti formula
- [Significato fisico]: cosa rappresenta
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
    
    def format_for_training(self, qa: dict, formula: str, formula_type: str) -> dict:
        """Format as training example"""
        return {
            "messages": [
                {
                    "role": "system",
                    "content": f"Sei ALL1E TUTOR, esperto educativo in {formula_type}. Spieghi formule con chiarezza e pedagogia."
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
                "formula_type": formula_type,
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
    
    async def generate_one_formula(self, formula: str, formula_type: str, semaphore, session) -> dict:
        """Generate explanation with ROBUST retry (max 3 attempts)"""
        async with semaphore:
            for attempt in range(self.max_retries):
                try:
                    prompt = self.create_prompt(formula, formula_type)
                    
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
                                return self.format_for_training(qa, formula, formula_type)
                        
                        # Retry on non-200 or invalid response
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                        
                except asyncio.TimeoutError:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1)
                except Exception:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(0.5)
            
            return None
    
    async def generate_async(self):
        """Generate formulas with 150 concurrent + retry logic"""
        print(f"\n{'='*80}\n🔬 FORMULAS GENERATOR - 150 CONCURRENT + RETRY\n{'='*80}")
        print(f"   Concurrent: {self.max_concurrent}")
        print(f"   Max retries per formula: {self.max_retries}")
        print(f"   Target: {self.target_count:,} valid examples")
        
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        all_data = checkpoint.get("all_data", [])
        
        if all_data:
            print(f"   ✅ Resuming from {len(all_data)} valid examples")
        
        # Load HuggingFace dataset
        print("\n📥 Loading HuggingFace dataset (streaming)...")
        ds = load_dataset('OleehyO/latex-formulas-80M', 'en', split='train', streaming=True)
        
        # Sample exactly 2,100 formulas (no waste)
        print("\n🔍 Sampling 2,100 formulas (no waste strategy)...")
        
        formulas_by_type = {
            "chemistry": [],
            "physics": [],
            "mathematics": []
        }
        
        sampled_count = {"chemistry": 0, "physics": 0, "mathematics": 0}
        
        for sample in ds:
            if all(sampled_count[t] >= self.targets[t] for t in self.targets):
                break
            
            latex = sample['latex_formula']
            if len(latex) < 10 or len(latex) > 500:
                continue
            
            ftype = self.classify_formula(latex)
            if sampled_count[ftype] < self.targets[ftype]:
                formulas_by_type[ftype].append(latex)
                sampled_count[ftype] += 1
        
        print(f"\n✅ Sampled formulas:")
        for ftype in formulas_by_type:
            print(f"   {ftype}: {len(formulas_by_type[ftype])} formulas")
        
        # Generate with retry until we reach target
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async with aiohttp.ClientSession() as session:
            for ftype, formulas in formulas_by_type.items():
                # Count how many valid examples we have for this type
                current_count = sum(1 for item in all_data if item['metadata']['formula_type'] == ftype)
                needed = self.targets[ftype] - current_count
                
                if needed <= 0:
                    print(f"\n✅ {ftype.upper()}: Already have {current_count}/{self.targets[ftype]}")
                    continue
                
                print(f"\n📊 Generating {ftype.upper()}: need {needed} more examples (150 concurrent + retry)...")
                
                # Shuffle formulas for diversity
                random.shuffle(formulas)
                
                # Generate ALL formulas with retry
                tasks = [
                    self.generate_one_formula(formula, ftype, semaphore, session)
                    for formula in formulas
                ]
                
                results = []
                for coro in async_tqdm(
                    asyncio.as_completed(tasks),
                    total=len(tasks),
                    desc=f"  {ftype}"
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
                
                print(f"   ✅ Generated {len(results)} valid examples for {ftype} (success rate: {len(results)/len(formulas)*100:.1f}%)")
        
        # Final save
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for item in all_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        self.save_checkpoint(all_data)
        
        print(f"\n✅ GENERATION COMPLETE: {len(all_data):,} valid examples")
        
        # Distribution
        by_type = {}
        for item in all_data:
            ftype = item['metadata']['formula_type']
            by_type[ftype] = by_type.get(ftype, 0) + 1
        
        print("\n📊 Final Distribution:")
        for ftype, count in by_type.items():
            target = self.targets[ftype]
            print(f"   {ftype}: {count}/{target} ({count/target*100:.1f}%)")
        
        return all_data

async def main():
    print("="*80 + "\n🔬 FORMULAS GENERATOR - 150 CONCURRENT + RETRY\n" + "="*80)
    generator = FormulasHFGeneratorRetry()
    await generator.generate_async()
    print("\n✅ ALL FORMULAS GENERATED SUCCESSFULLY")

if __name__ == "__main__":
    asyncio.run(main())
