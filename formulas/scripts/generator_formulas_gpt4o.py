"""
FORMULAS Generator - GPT-4o (NOT mini)
Target: 2,100 high-quality formula explanations
"""
import asyncio
import aiohttp
import json
from pathlib import Path
from tqdm.asyncio import tqdm as async_tqdm

class FormulasGPT4oGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_file = self.base_dir / "output" / "formulas_gpt4o.jsonl"
        self.checkpoint_file = self.base_dir / "checkpoints" / "formulas_gpt4o_checkpoint.json"
        self.output_file.parent.mkdir(exist_ok=True)
        self.checkpoint_file.parent.mkdir(exist_ok=True)
        
        self.api_key = "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"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "openai/gpt-4o"  # GPT-4o, NOT mini
        
        # Config
        self.max_concurrent = 400  # High concurrency
        self.max_retries = 3
        self.target_count = 2100
        
        # Common formulas by type
        self.chemistry_formulas = [
            r"$\mathrm{C_nH_{2n}O_n}$", r"$\mathrm{H_2O}$", r"$\mathrm{CO_2}$",
            r"$\mathrm{C_6H_{12}O_6}$", r"$\mathrm{NH_3}$", r"$\alpha(1 \rightarrow 4)$",
            r"$\beta(1 \rightarrow 4)$", r"$\mathrm{pH} = -\log[\mathrm{H^+}]$",
            r"$\Delta G = \Delta H - T\Delta S$", r"$K_a = \frac{[\mathrm{H^+}][\mathrm{A^-}]}{[\mathrm{HA}]}$",
            r"$K_w = [\mathrm{H^+}][\mathrm{OH^-}]$", r"$\mathrm{PV} = \mathrm{nRT}$",
            r"$\Delta H = \sum H_{products} - \sum H_{reactants}$", r"$\mathrm{CH_4}$",
            r"$\mathrm{NaCl}$", r"$\mathrm{HCl}$", r"$\mathrm{H_2SO_4}$",
            r"$\mathrm{CaCO_3}$", r"$\mathrm{Fe_2O_3}$", r"$\mathrm{AgNO_3}$"
        ]
        
        self.physics_formulas = [
            r"$F = ma$", r"$E = mc^2$", r"$v = v_0 + at$",
            r"$W = F \cdot d$", r"$P = \frac{F}{A}$", r"$E_k = \frac{1}{2}mv^2$",
            r"$Q = mc\Delta T$", r"$V = IR$", r"$F = G\frac{m_1m_2}{r^2}$",
            r"$\lambda = \frac{c}{f}$", r"$P = IV$", r"$E_p = mgh$",
            r"$\tau = F \cdot r$", r"$I = \frac{Q}{t}$", r"$p = mv$",
            r"$\omega = \frac{v}{r}$", r"$a_c = \frac{v^2}{r}$", r"$T = 2\pi\sqrt{\frac{L}{g}}$"
        ]
        
        self.math_formulas = [
            r"$\int x^n dx = \frac{x^{n+1}}{n+1} + C$", r"$\frac{d}{dx}(x^n) = nx^{n-1}$",
            r"$\lim_{x \to 0} \frac{\sin x}{x} = 1$", r"$a^2 + b^2 = c^2$",
            r"$e^{i\pi} + 1 = 0$", r"$\sum_{k=1}^{n} k = \frac{n(n+1)}{2}$",
            r"$\sin^2\theta + \cos^2\theta = 1$", r"$\frac{d}{dx}(e^x) = e^x$",
            r"$\int \frac{1}{x} dx = \ln|x| + C$", r"$\frac{d}{dx}(\ln x) = \frac{1}{x}$",
            r"$\int e^x dx = e^x + C$", r"$\lim_{n \to \infty} (1 + \frac{1}{n})^n = e$",
            r"$\tan\theta = \frac{\sin\theta}{\cos\theta}$", r"$\log_a(xy) = \log_a x + \log_a y$"
        ]
    
    def get_all_formulas(self):
        """Get all formulas with type labels"""
        formulas = []
        # 40% chemistry, 30% physics, 30% math
        chem_count = int(self.target_count * 0.4 / 5)  # 5 QA per formula
        phys_count = int(self.target_count * 0.3 / 5)
        math_count = int(self.target_count * 0.3 / 5)
        
        # Extend lists to reach target
        while len(self.chemistry_formulas) < chem_count:
            self.chemistry_formulas.extend(self.chemistry_formulas)
        while len(self.physics_formulas) < phys_count:
            self.physics_formulas.extend(self.physics_formulas)
        while len(self.math_formulas) < math_count:
            self.math_formulas.extend(self.math_formulas)
        
        for f in self.chemistry_formulas[:chem_count]:
            formulas.append((f, "chemistry"))
        for f in self.physics_formulas[:phys_count]:
            formulas.append((f, "physics"))
        for f in self.math_formulas[:math_count]:
            formulas.append((f, "mathematics"))
        
        return formulas
    
    def create_prompt(self, formula: str, formula_type: str) -> str:
        type_context = {
            "chemistry": "chimica organica e biochimica",
            "physics": "fisica e meccanica",
            "mathematics": "matematica e calcolo"
        }
        context = type_context.get(formula_type, "scienza")
        
        return f"""Sei un esperto educativo in {context}. Genera 5 conversazioni EDUCATIVE sulla formula:

{formula}

OUTPUT (JSON puro, no markdown):
[
  {{
    "question": "Domanda pedagogica sulla formula",
    "answer": "Spiegazione COMPLETA con:\\n- [Breakdown]: ogni simbolo\\n- [Significato]: concetto\\n- [Esempio pratico]: applicazione reale\\n- [Domande socratiche]: 2 domande\\n\\nLunghezza: 200-300 parole, italiano pedagogico"
  }}
]"""
    
    def parse_response(self, content: str) -> list:
        """Extract JSON array from API response"""
        try:
            # Remove markdown wrapper
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            content = content.strip()
            start = content.find('[')
            end = content.rfind(']') + 1
            
            if start != -1 and end > start:
                return json.loads(content[start:end])
        except:
            pass
        return []
    
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
                "source": "gpt4o_formulas"
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
    
    async def generate_one_formula(self, formula: str, formula_type: str, semaphore, session) -> list:
        """Generate 5 QA pairs with ROBUST retry (max 3 attempts)"""
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
                            "max_tokens": 6000
                        },
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        timeout=aiohttp.ClientTimeout(total=90)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            content = data['choices'][0]['message']['content']
                            qa_list = self.parse_response(content)
                            
                            # Validate and format
                            valid_results = []
                            for qa in qa_list:
                                if 'question' in qa and 'answer' in qa and len(qa['answer']) > 150:
                                    valid_results.append(self.format_for_training(qa, formula, formula_type))
                            
                            if valid_results:
                                return valid_results
                        
                        # Retry on non-200 or invalid response
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(0.5 * (attempt + 1))
                        
                except asyncio.TimeoutError:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1)
                except Exception:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(0.5)
            
            return []
    
    async def generate_async(self):
        """Generate formulas with 400 concurrent + retry logic"""
        print(f"\n{'='*80}\n🔬 GPT-4o FORMULAS GENERATOR\n{'='*80}")
        print(f"   Model: {self.model}")
        print(f"   Target: {self.target_count:,} examples")
        print(f"   Concurrent: {self.max_concurrent}")
        print(f"   Max retries: {self.max_retries}")
        
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        all_data = checkpoint.get("all_data", [])
        
        if all_data:
            print(f"   ✅ Resuming from {len(all_data)} valid examples")
        
        # Get all formulas
        print(f"\n📋 Preparing formulas (40% chemistry, 30% physics, 30% math)...")
        formulas = self.get_all_formulas()
        print(f"   ✅ {len(formulas)} formulas prepared")
        
        # Generate with retry until we reach target
        needed = self.target_count - len(all_data)
        print(f"\n📊 Need {needed} more valid examples (400 concurrent + retry)...")
        
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.generate_one_formula(formula, ftype, semaphore, session)
                for formula, ftype in formulas
            ]
            
            results = []
            for coro in async_tqdm(
                asyncio.as_completed(tasks),
                total=len(tasks),
                desc="  Generating"
            ):
                result = await coro
                if result:
                    results.extend(result)  # result is a list of QA pairs
                
                # Checkpoint every 100 valid
                if len(results) % 100 == 0 and len(results) > 0:
                    temp_data = all_data + results
                    self.save_checkpoint(temp_data)
                    
                    # Save to file
                    with open(self.output_file, 'w', encoding='utf-8') as f:
                        for item in temp_data[:self.target_count]:
                            f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
            # Add all valid results (limit to target)
            all_data.extend(results)
            all_data = all_data[:self.target_count]
        
        # Final save
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for item in all_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        self.save_checkpoint(all_data)
        
        # Stats
        by_type = {}
        for item in all_data:
            ftype = item['metadata']['formula_type']
            by_type[ftype] = by_type.get(ftype, 0) + 1
        
        print(f"\n✅ GENERATION COMPLETE: {len(all_data):,} valid examples")
        print(f"   Success rate: {len(results)/len(formulas)*5*100:.1f}%")  # 5 QA per formula
        print(f"\n📊 Distribution:")
        for ftype, count in by_type.items():
            print(f"   {ftype}: {count}")
        
        return all_data

async def main():
    print("="*80 + "\n🔬 GPT-4o FORMULAS GENERATOR\n" + "="*80)
    generator = FormulasGPT4oGenerator()
    await generator.generate_async()
    print("\n✅ ALL FORMULAS GENERATED SUCCESSFULLY")

if __name__ == "__main__":
    asyncio.run(main())
