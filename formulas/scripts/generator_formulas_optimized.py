"""
FORMULAS Generator OPTIMIZED - Chemistry, Physics, Mathematics
LEVEL 9 Optimizations: Asyncio + Checkpoint + 200 concurrent
"""
import json, time, asyncio
from pathlib import Path
from typing import List, Dict
from tqdm.asyncio import tqdm as async_tqdm
from openrouter_client import OpenRouterClient

class FormulasGeneratorOptimized:
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
        
        # LEVEL 9 Optimizations
        self.max_concurrent = 200  # MASSIMO PARALLELISMO
        self.batch_save = 100  # Save every 100 examples
        
        # Output setup
        self.base_dir = Path(__file__).parent
        self.output_file = self.base_dir / "output" / "formulas.jsonl"
        self.checkpoint_file = self.base_dir / "checkpoints" / "formulas_checkpoint.json"
        self.checkpoint_file.parent.mkdir(exist_ok=True)
        
        # Common formulas by type
        self.chemistry_formulas = [
            r"$\mathrm{C_nH_{2n}O_n}$", r"$\mathrm{H_2O}$", r"$\mathrm{CO_2}$",
            r"$\mathrm{C_6H_{12}O_6}$", r"$\mathrm{NH_3}$", r"$\alpha(1 \rightarrow 4)$",
            r"$\beta(1 \rightarrow 4)$", r"$\mathrm{pH} = -\log[\mathrm{H^+}]$",
            r"$\Delta G = \Delta H - T\Delta S$", r"$K_a = \frac{[\mathrm{H^+}][\mathrm{A^-}]}{[\mathrm{HA}]}$"
        ]
        
        self.physics_formulas = [
            r"$F = ma$", r"$E = mc^2$", r"$v = v_0 + at$", r"$W = F \cdot d$",
            r"$P = \frac{F}{A}$", r"$E_k = \frac{1}{2}mv^2$", r"$Q = mc\Delta T$",
            r"$V = IR$", r"$F = G\frac{m_1m_2}{r^2}$", r"$\lambda = \frac{c}{f}$"
        ]
        
        self.math_formulas = [
            r"$\int x^n dx = \frac{x^{n+1}}{n+1} + C$", r"$\frac{d}{dx}(x^n) = nx^{n-1}$",
            r"$\lim_{x \to 0} \frac{\sin x}{x} = 1$", r"$a^2 + b^2 = c^2$",
            r"$e^{i\pi} + 1 = 0$", r"$\sum_{k=1}^{n} k = \frac{n(n+1)}{2}$",
            r"$\sin^2\theta + \cos^2\theta = 1$", r"$\vec{F} = m\vec{a}$",
            r"$\frac{d}{dx}(e^x) = e^x$", r"$\int \frac{1}{x} dx = \ln|x| + C$"
        ]
        
        self.completed = 0
    
    def load_checkpoint(self) -> Dict:
        """Load last checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return {"completed": 0, "formulas_done": [], "all_data": []}
    
    def save_checkpoint(self, formulas_done: List[str], all_data: List[Dict]):
        """Save checkpoint"""
        state = {
            "completed": len(all_data),
            "formulas_done": formulas_done,
            "all_data": all_data
        }
        with open(self.checkpoint_file, "w") as f:
            json.dump(state, f, indent=2)
    
    def create_prompt(self, formula: str, formula_type: str) -> str:
        type_context = {
            "chemistry": "chimica organica e biochimica",
            "physics": "fisica e meccanica",
            "mathematics": "matematica e calcolo"
        }
        
        context = type_context.get(formula_type, "scienza")
        
        return f"""Sei un esperto educativo in {context}. Genera 5 conversazioni EDUCATIVE sulla formula:

{formula}

OUTPUT (JSON):
[
  {{
    "question": "Domanda pedagogica sulla formula (cosa significa, quando si usa, come si applica)",
    "answer": "Spiegazione ECCELLENTE che:\\n1. Breakdown della formula (ogni simbolo/termine)\\n2. Significato fisico/chimico/matematico\\n3. Esempi pratici di applicazione\\n4. 1-2 domande socratiche\\n5. Tono pedagogico, chiaro, incoraggiante\\n6. Lunghezza: 200-250 parole"
  }}
]

ESEMPIO QUALITÀ:

DOMANDA ECCELLENTE: "Come la seconda legge di Newton $F=ma$ spiega perché è più difficile spingere un'auto che una bicicletta?"

RISPOSTA ECCELLENTE: "La seconda legge di Newton $F=ma$ ci dice che la forza necessaria per accelerare un oggetto dipende da due fattori: la massa dell'oggetto e quanto rapidamente vogliamo che acceleri.

[Breakdown] 
- $F$: Forza applicata (Newton, N)
- $m$: Massa dell'oggetto (kg) - resistenza al movimento
- $a$: Accelerazione desiderata (m/s²)

[Significato fisico] Massa più grande = più forza necessaria per stessa accelerazione. Questo spiega perché spingere un'auto (massa ~1500 kg) richiede MOLTO più sforzo di una bici (massa ~15 kg) per ottenere la stessa accelerazione.

[Esempio pratico] Immagina di spingere entrambe con forza di 100N:
- Bicicletta: $a = F/m = 100/15 = 6.67$ m/s² (accelera rapidamente!)
- Auto: $a = F/m = 100/1500 = 0.067$ m/s² (appena si muove)

[Domande socratiche] Cosa succederebbe se la massa fosse zero? Come questa legge si applica al lancio di razzi spaziali?

Questa legge è fondamentale per capire ogni tipo di movimento!"

REGOLE:
1. Breakdown completo della formula
2. Esempi numerici concreti
3. Applicazioni reali
4. Domande socratiche per stimolare
5. Tono pedagogico sempre

Genera 5 conversazioni ECCELLENTI sulla formula {formula}."""
    
    def parse_response(self, response: str):
        import re
        try:
            if response.strip().startswith('['):
                return json.loads(response)
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return []
        except:
            return []
    
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
                "source": "synthetic_formulas"
            }
        }
    
    async def generate_one_formula(self, formula: str, formula_type: str, semaphore) -> List[Dict]:
        """Generate QA for one formula (async)"""
        async with semaphore:
            prompt = self.create_prompt(formula, formula_type)
            try:
                messages = [{"role": "user", "content": prompt}]
                # Sync call wrapped in async
                response = await asyncio.to_thread(
                    self.client.generate,
                    messages,
                    temperature=0.7,
                    max_tokens=6000
                )
                qa_list = self.parse_response(response)
                return [
                    self.format_for_training(qa, formula, formula_type) 
                    for qa in qa_list 
                    if 'question' in qa and 'answer' in qa and len(qa['answer']) > 200
                ]
            except Exception as e:
                print(f"❌ Error on {formula}: {e}")
                return []
    
    async def generate_async(self, target: int):
        """Main async generation loop"""
        print(f"\n{'='*80}\n📝 Generating {target} formula explanations (LEVEL 9 OPTIMIZED)\n{'='*80}")
        print(f"   Max concurrent: {self.max_concurrent}")
        
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        all_data = checkpoint.get("all_data", [])
        formulas_done = set(checkpoint.get("formulas_done", []))
        
        if all_data:
            print(f"   ✅ Resuming from {len(all_data)} examples")
        
        # Distribution: 40% chemistry, 30% physics, 30% math
        targets = {
            "chemistry": int(target * 0.4),
            "physics": int(target * 0.3),
            "mathematics": int(target * 0.3)
        }
        
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        for formula_type, type_target in targets.items():
            if len(all_data) >= target:
                break
                
            print(f"\n📊 Generating for: {formula_type.upper()} (target: {type_target})")
            
            # Get formula list
            if formula_type == "chemistry":
                formulas = self.chemistry_formulas
            elif formula_type == "physics":
                formulas = self.physics_formulas
            else:
                formulas = self.math_formulas
            
            # Extend list if needed
            while len(formulas) * 5 < type_target:
                formulas = formulas + formulas
            
            # Filter out done formulas
            formulas_to_process = [
                (formula, formula_type) 
                for formula in formulas 
                if f"{formula_type}:{formula}" not in formulas_done
            ]
            
            # Create tasks (all at once for max concurrency)
            tasks = [
                self.generate_one_formula(formula, ftype, semaphore)
                for formula, ftype in formulas_to_process[:type_target // 5]
            ]
            
            # Execute with progress bar
            results = []
            for coro in async_tqdm(
                asyncio.as_completed(tasks),
                total=len(tasks),
                desc=f"  {formula_type}"
            ):
                result = await coro
                if result:
                    results.extend(result)
                    formulas_done.add(f"{formula_type}:{formulas_to_process[len(results)//5][0]}")
                
                # Checkpoint every 100 examples
                if len(all_data) + len(results) % 100 < 5:
                    all_data.extend(results)
                    self.save_checkpoint(list(formulas_done), all_data)
                    results = []
                    
                    # Save to file
                    with open(self.output_file, 'w', encoding='utf-8') as f:
                        for item in all_data[:target]:
                            f.write(json.dumps(item, ensure_ascii=False) + '\n')
                    print(f"   💾 Saved {len(all_data)}")
            
            # Add remaining
            all_data.extend(results)
        
        # Final save
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for item in all_data[:target]:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        self.save_checkpoint(list(formulas_done), all_data[:target])
        
        print(f"\n✅ Generated {len(all_data[:target])} formula explanations")
        
        # Stats
        by_type = {}
        for item in all_data[:target]:
            ftype = item['metadata']['formula_type']
            by_type[ftype] = by_type.get(ftype, 0) + 1
        
        print("\n📊 Distribution:")
        for ftype, count in by_type.items():
            print(f"   {ftype}: {count}")
        
        return all_data[:target]

async def main():
    print("="*80 + "\n🔬 FORMULAS GENERATOR OPTIMIZED - LEVEL 9\n" + "="*80)
    generator = FormulasGeneratorOptimized()
    await generator.generate_async(2100)  # Original target
    print("\n✅ FORMULAS GENERATION COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())
