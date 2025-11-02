"""
FORMULAS Generator - Chemistry, Physics, Mathematics
Generates educational Q&A on LaTeX formulas
"""
import json, time, random
from openrouter_client import OpenRouterClient
from tqdm import tqdm

class FormulasGenerator:
    def __init__(self):
        # Use new OpenRouter key
        from dataclasses import dataclass
        @dataclass
        class CustomConfig:
            api_key: str = "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"
            base_url: str = "https://openrouter.ai/api/v1/chat/completions"
            model: str = "openai/gpt-4o-mini"
            temperature: float = 0.7
            max_tokens: int = 4000
        
        self.client = OpenRouterClient(CustomConfig())
        
        # Common formulas by type
        self.chemistry_formulas = [
            r"$\mathrm{C_nH_{2n}O_n}$",
            r"$\mathrm{H_2O}$",
            r"$\mathrm{CO_2}$",
            r"$\mathrm{C_6H_{12}O_6}$",
            r"$\mathrm{NH_3}$",
            r"$\alpha(1 \rightarrow 4)$",
            r"$\beta(1 \rightarrow 4)$",
            r"$\mathrm{pH} = -\log[\mathrm{H^+}]$",
            r"$\Delta G = \Delta H - T\Delta S$",
            r"$K_a = \frac{[\mathrm{H^+}][\mathrm{A^-}]}{[\mathrm{HA}]}$"
        ]
        
        self.physics_formulas = [
            r"$F = ma$",
            r"$E = mc^2$",
            r"$v = v_0 + at$",
            r"$W = F \cdot d$",
            r"$P = \frac{F}{A}$",
            r"$E_k = \frac{1}{2}mv^2$",
            r"$Q = mc\Delta T$",
            r"$V = IR$",
            r"$F = G\frac{m_1m_2}{r^2}$",
            r"$\lambda = \frac{c}{f}$"
        ]
        
        self.math_formulas = [
            r"$\int x^n dx = \frac{x^{n+1}}{n+1} + C$",
            r"$\frac{d}{dx}(x^n) = nx^{n-1}$",
            r"$\lim_{x \to 0} \frac{\sin x}{x} = 1$",
            r"$a^2 + b^2 = c^2$",
            r"$e^{i\pi} + 1 = 0$",
            r"$\sum_{k=1}^{n} k = \frac{n(n+1)}{2}$",
            r"$\sin^2\theta + \cos^2\theta = 1$",
            r"$\vec{F} = m\vec{a}$",
            r"$\frac{d}{dx}(e^x) = e^x$",
            r"$\int \frac{1}{x} dx = \ln|x| + C$"
        ]
    
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

DOMANDA MEDIOCRE: "Cosa significa $F=ma$?"
DOMANDA ECCELLENTE: "Come la seconda legge di Newton $F=ma$ spiega perché è più difficile spingere un'auto che una bicicletta?"

RISPOSTA MEDIOCRE: "F è forza, m è massa, a è accelerazione. Forza uguale massa per accelerazione."
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
    
    def generate_batch(self, formula: str, formula_type: str):
        prompt = self.create_prompt(formula, formula_type)
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.generate(messages, temperature=0.7, max_tokens=6000)
            qa_list = self.parse_response(response)
            return [self.format_for_training(qa, formula, formula_type) for qa in qa_list if 'question' in qa and 'answer' in qa and len(qa['answer']) > 200]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate(self, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} formula explanations\n{'='*80}")
        
        # Distribution: 40% chemistry, 30% physics, 30% math
        targets = {
            "chemistry": int(target * 0.4),
            "physics": int(target * 0.3),
            "mathematics": int(target * 0.3)
        }
        
        all_formulas_data = []
        
        for formula_type, type_target in targets.items():
            print(f"\n📊 Generating {type_target} for: {formula_type.upper()}")
            
            # Get formula list
            if formula_type == "chemistry":
                formulas = self.chemistry_formulas
            elif formula_type == "physics":
                formulas = self.physics_formulas
            else:
                formulas = self.math_formulas
            
            # Extend list if needed
            while len(formulas) * 5 < type_target:  # 5 QA per formula
                formulas = formulas + formulas
            
            generated_count = 0
            
            for formula in tqdm(formulas, desc=f"  {formula_type}"):
                if generated_count >= type_target:
                    break
                
                batch = self.generate_batch(formula, formula_type)
                all_formulas_data.extend(batch)
                generated_count += len(batch)
                
                if generated_count % 100 == 0:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for item in all_formulas_data:
                            f.write(json.dumps(item, ensure_ascii=False) + '\n')
                    print(f"   💾 Saved {len(all_formulas_data)}")
                
                time.sleep(0.1)  # Optimized
        
        # Final save
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in all_formulas_data[:target]:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Generated {len(all_formulas_data[:target])} formula explanations")
        
        # Stats
        by_type = {}
        for item in all_formulas_data[:target]:
            ftype = item['metadata']['formula_type']
            by_type[ftype] = by_type.get(ftype, 0) + 1
        
        print("\n📊 Distribution:")
        for ftype, count in by_type.items():
            print(f"   {ftype}: {count}")
        
        return all_formulas_data[:target]

def main():
    print("="*80 + "\n🔬 FORMULAS GENERATOR - Chemistry, Physics, Mathematics\n" + "="*80)
    generator = FormulasGenerator()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2_dataset_generation/output"
    output = f"{output_dir}/formulas.jsonl"
    generator.generate(7000, output)
    print("\n✅ FORMULAS GENERATION COMPLETE")

if __name__ == "__main__":
    main()
