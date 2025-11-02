"""FUNCTION CALLING Generator - plotting_tool per grafici matematici"""
import json, time
from openrouter_client import OpenRouterClient
from tqdm import tqdm

class FunctionCallingGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, topic: str) -> str:
        return f"""Sei ALL1E TUTOR con capacità di plotting matematico.

Genera 10 problemi di {topic} che richiedono visualizzazione grafica.

OUTPUT (JSON):
[
  {{
    "problem": "Problema completo con contesto realistico (ingegneria, fisica, economia) che richiede analisi grafica della funzione",
    "solution": "### Introduzione\\nContesto del problema...\\n\\n### [FUNCTION_CALL: plotting_tool]\\n\\n### Analisi matematica del grafico\\nAnalisi dettagliata con calcoli, interpretazione grafica, applicazioni pratiche",
    "function_call": {{
      "name": "plotting_tool",
      "arguments": {{
        "expression": "funzione matematica (es: sin(x), x**2, tan(x))",
        "x_range": [-10, 10]
      }}
    }},
    "func_type": "trig/polynomial/exponential/logarithmic"
  }}
]

TOPICS DISPONIBILI:
- Funzioni trigonometriche (sin, cos, tan)
- Funzioni polinomiali (x^2, x^3)
- Funzioni esponenziali (e^x, 2^x)
- Funzioni logaritmiche (log(x), ln(x))
- Funzioni razionali (1/x, (x+1)/(x-2))

REGOLE:
1. Problem: Contesto realistico applicato
2. Solution: Introduzione + [FUNCTION_CALL] + Analisi grafico
3. function_call: plotting_tool con expression e x_range
4. Analisi matematica dettagliata basata sul grafico

Genera 10 problemi di {topic}."""
    
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
    
    def format_for_training(self, func: dict) -> dict:
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "Sei ALL1E TUTOR. Usa plotting_tool per grafici."
                },
                {
                    "role": "user",
                    "content": func['problem']
                },
                {
                    "role": "assistant",
                    "content": func['solution']
                }
            ],
            "function_calls": [func['function_call']],
            "metadata": {
                "type": "function_calling",
                "func_type": func['func_type'],
                "source": "generated_math_problems"
            }
        }
    
    def generate_batch(self, topic: str):
        prompt = self.create_prompt(topic)
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.generate(messages, temperature=0.7, max_tokens=8000)
            func_list = self.parse_response(response)
            return [self.format_for_training(f) for f in func_list if all(k in f for k in ['problem', 'solution', 'function_call'])]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate(self, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} function calling examples\n{'='*80}")
        
        topics = [
            "funzioni trigonometriche",
            "funzioni polinomiali",
            "funzioni esponenziali",
            "funzioni logaritmiche",
            "funzioni razionali"
        ]
        
        all_functions = []
        
        for topic in tqdm(topics, desc="Topics"):
            needed = target // len(topics)
            
            while len([f for f in all_functions if topic in str(f)]) < needed:
                batch = self.generate_batch(topic)
                all_functions.extend(batch)
                
                if len(all_functions) % 50 == 0:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for func in all_functions:
                            f.write(json.dumps(func, ensure_ascii=False) + '\n')
                    print(f"   💾 Saved {len(all_functions)}")
                time.sleep(0.1)  # Optimized
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for func in all_functions[:target]:
                f.write(json.dumps(func, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Generated {len(all_functions[:target])} function calling examples")
        return all_functions[:target]

def main():
    print("="*80 + "\n🚀 FUNCTION CALLING GENERATOR\n" + "="*80)
    generator = FunctionCallingGenerator()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2_dataset_generation/output"
    output = f"{output_dir}/function_calling.jsonl"
    generator.generate(5000, output)
    print("\n✅ FUNCTION CALLING GENERATION COMPLETE")

if __name__ == "__main__":
    main()
