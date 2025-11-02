"""
Formulas Generator from HuggingFace Dataset
Uses OleehyO/latex-formulas-80M + OpenRouter GPT-4o-mini
Target: 2,100 high-quality educational formula explanations
"""
import json, re, asyncio
from pathlib import Path
from typing import List, Dict
from tqdm.asyncio import tqdm as async_tqdm
from datasets import load_dataset
from openrouter_client import OpenRouterClient

class FormulasHFGenerator:
    def __init__(self):
        from dataclasses import dataclass
        @dataclass
        class CustomConfig:
            api_key: str = "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"
            base_url: str = "https://openrouter.ai/api/v1/chat/completions"
            model: str = "openai/gpt-4o-mini"
            temperature: float = 0.7
            max_tokens: int = 4000
        
        self.client = OpenRouterClient(CustomConfig())
        self.base_dir = Path(__file__).parent
        self.output_file = self.base_dir / "output" / "formulas_hf.jsonl"
        self.checkpoint_file = self.base_dir / "checkpoints" / "formulas_hf_checkpoint.json"
        self.checkpoint_file.parent.mkdir(exist_ok=True)
        
        # LEVEL 9 optimizations (reduced for stability)
        self.max_concurrent = 100
        self.batch_save = 50
        
        # Targets (40% chem, 30% phys, 30% math)
        self.targets = {
            "chemistry": 840,
            "physics": 630,
            "mathematics": 630
        }
        
        # Classification patterns
        self.chem_patterns = [
            r'\\ce\{', r'\\rightarrow', r'\\leftarrow', r'\\leftrightarrow',
            r'H_2O', r'CO_2', r'NH_3', r'CH_', r'C_\d+H', r'_{aq}', r'_{(s|l|g)}',
            r'[A-Z][a-z]?_\d+', r'mol', r'pH', r'pK', r'\Delta G', r'\Delta H'
        ]
        
        self.phys_patterns = [
            r'\\vec\{', r'\\hat\{', r'F\s*=\s*m', r'E\s*=\s*m', r'v\s*=',
            r'\\omega', r'\\lambda', r'\\nu', r'\\rho', r'\\sigma',
            r'kg', r'm/s', r'N\s', r'J\s', r'W\s', r'Hz', r'Pa',
            r'\\nabla', r'\\partial', r'\\dot\{', r'\\ddot\{'
        ]
        
        self.math_patterns = [
            r'\\int', r'\\sum', r'\\prod', r'\\lim', r'\\frac\{d',
            r'\\infty', r'\\forall', r'\\exists', r'\\in\s*\\mathbb',
            r'\\sin', r'\\cos', r'\\tan', r'\\log', r'\\ln', r'\\exp',
            r'\\theta', r'\\alpha', r'\\beta', r'\\gamma', r'\\pi'
        ]
    
    def classify_formula(self, latex: str) -> str:
        """Classify formula by content"""
        chem_score = sum(1 for p in self.chem_patterns if re.search(p, latex))
        phys_score = sum(1 for p in self.phys_patterns if re.search(p, latex))
        math_score = sum(1 for p in self.math_patterns if re.search(p, latex))
        
        scores = {"chemistry": chem_score, "physics": phys_score, "mathematics": math_score}
        return max(scores, key=scores.get) if max(scores.values()) > 0 else "mathematics"
    
    def load_checkpoint(self) -> Dict:
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return {"completed": {"chemistry": 0, "physics": 0, "mathematics": 0}, "all_data": []}
    
    def save_checkpoint(self, completed: Dict, all_data: List[Dict]):
        with open(self.checkpoint_file, "w") as f:
            json.dump({"completed": completed, "all_data": all_data}, f, indent=2)
    
    def create_prompt(self, formula: str, formula_type: str) -> str:
        type_context = {
            "chemistry": "chimica e reazioni",
            "physics": "fisica e leggi della natura",
            "mathematics": "matematica e calcolo"
        }
        
        return f"""Sei un esperto educativo in {type_context[formula_type]}. Genera UNA conversazione educativa sulla formula:

{formula}

OUTPUT (JSON singolo):
{{
  "question": "Domanda pedagogica sulla formula (cosa significa, quando si usa, come si applica)",
  "answer": "Spiegazione ECCELLENTE che:\\n1. Breakdown della formula (ogni simbolo/termine)\\n2. Significato fisico/chimico/matematico\\n3. Esempi pratici di applicazione\\n4. 1-2 domande socratiche\\n5. Tono pedagogico, chiaro, incoraggiante\\n6. Lunghezza: 200-250 parole"
}}

ESEMPIO:
{{
  "question": "Come la seconda legge di Newton $F=ma$ spiega perché è più difficile spingere un'auto che una bicicletta?",
  "answer": "La seconda legge di Newton $F=ma$ ci dice che la forza necessaria per accelerare un oggetto dipende da due fattori: la massa dell'oggetto e quanto rapidamente vogliamo che acceleri.\\n\\n[Breakdown]\\n- $F$: Forza applicata (Newton, N)\\n- $m$: Massa dell'oggetto (kg)\\n- $a$: Accelerazione desiderata (m/s²)\\n\\n[Significato fisico] Massa più grande = più forza necessaria. Questo spiega perché spingere un'auto (1500 kg) richiede MOLTO più sforzo di una bici (15 kg).\\n\\n[Esempio pratico] Con forza di 100N:\\n- Bicicletta: $a = 100/15 = 6.67$ m/s²\\n- Auto: $a = 100/1500 = 0.067$ m/s²\\n\\n[Domande socratiche] Cosa succederebbe se la massa fosse zero? Come si applica ai razzi spaziali?"
}}

Genera SOLO UN JSON per la formula: {formula}"""
    
    def parse_response(self, response: str) -> Dict:
        try:
            if response.strip().startswith('{'):
                return json.loads(response)
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return {}
        except:
            return {}
    
    def format_for_training(self, qa: dict, formula: str, formula_type: str) -> dict:
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
            "formula_data": {
                "formula": formula,
                "type": formula_type
            },
            "metadata": {
                "type": "formula_explanation",
                "formula_type": formula_type,
                "source": "huggingface_80M"
            }
        }
    
    async def generate_one_formula(self, formula: str, formula_type: str, semaphore) -> Dict:
        """Generate educational explanation for one formula"""
        async with semaphore:
            try:
                prompt = self.create_prompt(formula, formula_type)
                messages = [{"role": "user", "content": prompt}]
                response = await asyncio.to_thread(
                    self.client.generate,
                    messages,
                    temperature=0.7,
                    max_tokens=3000
                )
                qa = self.parse_response(response)
                if 'question' in qa and 'answer' in qa and len(qa['answer']) > 150:
                    return self.format_for_training(qa, formula, formula_type)
            except Exception as e:
                print(f"❌ Error on formula: {e}")
            return None
    
    async def generate_async(self):
        print(f"\n{'='*80}\n📝 Generating 2,100 formulas from HuggingFace (LEVEL 9)\n{'='*80}")
        print(f"   Max concurrent: {self.max_concurrent}")
        print(f"   Source: OleehyO/latex-formulas-80M")
        
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        all_data = checkpoint.get("all_data", [])
        completed = checkpoint.get("completed", {"chemistry": 0, "physics": 0, "mathematics": 0})
        
        if all_data:
            print(f"   ✅ Resuming from {len(all_data)} examples")
        
        # Load HF dataset (streaming)
        print("\n📥 Loading HuggingFace dataset...")
        ds = load_dataset('OleehyO/latex-formulas-80M', 'en', split='train', streaming=True)
        
        # Collect formulas by type
        formulas_by_type = {"chemistry": [], "physics": [], "mathematics": []}
        
        print("\n🔍 Classifying and sampling formulas...")
        for sample in ds:
            # Check if we have enough
            if all(completed[t] >= self.targets[t] for t in self.targets):
                break
            
            latex = sample['latex_formula']
            if len(latex) < 10 or len(latex) > 500:  # Filter too short/long
                continue
            
            ftype = self.classify_formula(latex)
            if completed[ftype] < self.targets[ftype]:
                formulas_by_type[ftype].append(latex)
                completed[ftype] += 1
        
        print(f"\n✅ Sampled formulas:")
        for ftype, formulas in formulas_by_type.items():
            print(f"   {ftype}: {len(formulas)}/{self.targets[ftype]}")
        
        # Generate explanations
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        for ftype, formulas in formulas_by_type.items():
            print(f"\n📊 Generating {ftype.upper()} explanations...")
            
            tasks = [
                self.generate_one_formula(formula, ftype, semaphore)
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
                
                # Checkpoint every 50
                if len(results) % 50 == 0 and len(results) > 0:
                    all_data.extend(results)
                    self.save_checkpoint(completed, all_data)
                    
                    # Save to file
                    with open(self.output_file, 'w', encoding='utf-8') as f:
                        for item in all_data:
                            f.write(json.dumps(item, ensure_ascii=False) + '\n')
                    
                    results = []
            
            # Add remaining
            all_data.extend(results)
        
        # Final save
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for item in all_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        self.save_checkpoint(completed, all_data)
        
        print(f"\n✅ Generated {len(all_data)} formula explanations")
        
        # Stats
        by_type = {}
        for item in all_data:
            ftype = item['metadata']['formula_type']
            by_type[ftype] = by_type.get(ftype, 0) + 1
        
        print("\n📊 Distribution:")
        for ftype, count in by_type.items():
            print(f"   {ftype}: {count}")
        
        return all_data

async def main():
    print("="*80 + "\n🔬 FORMULAS GENERATOR - HUGGINGFACE 80M\n" + "="*80)
    generator = FormulasHFGenerator()
    await generator.generate_async()
    print("\n✅ FORMULAS GENERATION COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())
