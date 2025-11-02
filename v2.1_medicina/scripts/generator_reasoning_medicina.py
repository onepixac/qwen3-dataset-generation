"""
REASONING Generator MEDICINA - Casi clinici con diagnosi differenziale
Target: 8,000 esempi da 26 libri Secrets/WAU
"""
import json, time
from openrouter_client import OpenRouterClient
from load_secrets_books import prepare_for_generation
from tqdm import tqdm
import re

class ReasoningMedicinaGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, chunk: str, specialty: str) -> str:
        return f"""Genera 10 casi clinici con ragionamento diagnostico su {specialty.upper()}.

CONTENUTO CLINICO:
{chunk[:3000]}

OUTPUT (JSON array):
[
  {{
    "clinical_case": "Caso clinico con sintomi/segni/esami (paziente realistico)",
    "question": "Qual è la diagnosi più probabile e il ragionamento diagnostico?",
    "reasoning": "Ragionamento clinico: 1) Analisi sintomi, 2) Diagnosi differenziale (almeno 3 ipotesi), 3) Esami di conferma, 4) Conclusione diagnostica (200-250 parole)"
  }}
]

Genera 10 casi con DD completa."""
    
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
    
    def format_for_training(self, case: dict, specialty: str) -> dict:
        return {
            "messages": [
                {"role": "system", "content": "Sei ALL1E TUTOR MEDICINA per ragionamento clinico."},
                {"role": "user", "content": f"Caso clinico:\n{case['clinical_case']}\n\n{case['question']}"},
                {"role": "assistant", "content": case['reasoning']}
            ],
            "metadata": {
                "type": "medicina_reasoning_dd",
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
            response = self.client.generate(messages, temperature=0.8, max_tokens=10000)
            case_list = self.parse_response(response)
            return [self.format_for_training(c, specialty) for c in case_list if 'clinical_case' in c and 'reasoning' in c]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate_all(self, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} medicina reasoning\n{'='*80}")
        data = prepare_for_generation()
        chunks = data['chunks']
        all_cases = []
        
        for chunk in tqdm(chunks, desc="  Medicina Reasoning"):
            if len(all_cases) >= target:
                break
            specialty = chunk.get('specialty', 'medicina')
            batch = self.generate_batch(chunk['text'], specialty)
            all_cases.extend(batch)
            if len(all_cases) % 100 == 0:
                with open(output_path, 'w', encoding='utf-8') as f:
                    for c in all_cases:
                        f.write(json.dumps(c, ensure_ascii=False) + '\n')
                print(f"   💾 Saved {len(all_cases)}")
            time.sleep(0.1)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for c in all_cases[:target]:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
        print(f"\n✅ Generated {len(all_cases[:target])} reasoning")
        return all_cases[:target]

def main():
    print("="*80 + "\n🚀 MEDICINA REASONING GENERATOR\n" + "="*80)
    generator = ReasoningMedicinaGenerator()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2.1_generation/output"
    generator.generate_all(8000, f"{output_dir}/reasoning_medicina.jsonl")
    print("\n✅ REASONING GENERATION COMPLETE")

if __name__ == "__main__":
    main()
