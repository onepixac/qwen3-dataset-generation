"""
VARIETY Generator MEDICINA - Scenari clinici complessi multi-step
Target: 4,000 esempi da 26 libri Secrets/WAU
"""
import json, time
from openrouter_client import OpenRouterClient
from load_secrets_books import prepare_for_generation
from tqdm import tqdm
import re

class VarietyMedicinaGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, chunk: str, specialty: str) -> str:
        return f"""Genera 10 scenari clinici complessi multi-step su {specialty.upper()}.

CONTENUTO CLINICO:
{chunk[:3000]}

OUTPUT (JSON array):
[
  {{
    "scenario": "Scenario clinico complesso con evoluzione temporale (paziente realistico)",
    "question": "Domanda multi-step che richiede: 1) Analisi iniziale, 2) Diagnosi differenziale, 3) Piano terapeutico",
    "analysis": "Analisi multi-step:\\n\\nSTEP 1 - Analisi iniziale: [valutazione sintomi/segni]\\n\\nSTEP 2 - Diagnosi differenziale: [3+ ipotesi con ragionamento]\\n\\nSTEP 3 - Piano terapeutico: [gestione immediata + follow-up]\\n\\n(250-300 parole totali)"
  }}
]

Genera 10 scenari complessi multi-step."""
    
    def sanitize_json_text(self, text: str) -> str:
        return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', ' ', text)
    
    def parse_response(self, response: str):
        try:
            response = self.sanitize_json_text(response)
            if response.strip().startswith('['):
                return json.loads(response)
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return []
        except Exception as e:
            print(f"   ⚠️ JSON parse error: {e}")
            return []
    
    def format_for_training(self, scenario: dict, specialty: str) -> dict:
        return {
            "messages": [
                {"role": "system", "content": "Sei ALL1E TUTOR MEDICINA per scenari complessi."},
                {"role": "user", "content": f"Scenario:\n{scenario['scenario']}\n\n{scenario['question']}"},
                {"role": "assistant", "content": scenario['analysis']}
            ],
            "metadata": {
                "type": "medicina_variety_multistep",
                "specialty": specialty,
                "source": "secrets_wau_textbooks",
                "quality": "excellent"
            }
        }
    
    def generate_batch(self, chunk_text: str, specialty: str):
        chunk_text = self.sanitize_json_text(chunk_text)
        prompt = self.create_prompt(chunk_text, specialty)
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.generate(messages, temperature=0.8, max_tokens=12000)
            scenario_list = self.parse_response(response)
            return [self.format_for_training(s, specialty) for s in scenario_list if 'scenario' in s and 'analysis' in s]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate_all(self, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} medicina variety\n{'='*80}")
        data = prepare_for_generation()
        chunks = data['chunks']
        all_scenarios = []
        
        for chunk in tqdm(chunks, desc="  Medicina Variety"):
            if len(all_scenarios) >= target:
                break
            specialty = chunk.get('specialty', 'medicina')
            batch = self.generate_batch(chunk['text'], specialty)
            all_scenarios.extend(batch)
            if len(all_scenarios) % 100 == 0:
                with open(output_path, 'w', encoding='utf-8') as f:
                    for s in all_scenarios:
                        f.write(json.dumps(s, ensure_ascii=False) + '\n')
                print(f"   💾 Saved {len(all_scenarios)}")
            time.sleep(0.1)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for s in all_scenarios[:target]:
                f.write(json.dumps(s, ensure_ascii=False) + '\n')
        print(f"\n✅ Generated {len(all_scenarios[:target])} variety")
        return all_scenarios[:target]

def main():
    print("="*80 + "\n🚀 MEDICINA VARIETY GENERATOR\n" + "="*80)
    generator = VarietyMedicinaGenerator()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2.1_generation/output"
    generator.generate_all(4000, f"{output_dir}/variety_medicina.jsonl")
    print("\n✅ VARIETY GENERATION COMPLETE")

if __name__ == "__main__":
    main()
