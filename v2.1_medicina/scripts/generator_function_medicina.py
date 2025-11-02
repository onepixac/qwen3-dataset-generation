"""
FUNCTION CALLING Generator MEDICINA - Calcoli clinici (GFR, BMI, score)
Target: 4,000 esempi da 26 libri Secrets/WAU
"""
import json, time
from openrouter_client import OpenRouterClient
from load_secrets_books import prepare_for_generation
from tqdm import tqdm
import re

class FunctionMedicinaGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, chunk: str, specialty: str) -> str:
        return f"""Genera 10 esempi di calcoli clinici su {specialty.upper()}.

CONTENUTO CLINICO:
{chunk[:3000]}

OUTPUT (JSON array):
[
  {{
    "request": "Richiesta di calcolo: GFR, BMI, CURB-65, CHA2DS2-VASc, score APACHE, ecc.",
    "calculation": "Formula utilizzata + valori inseriti + calcolo step-by-step",
    "interpretation": "Interpretazione clinica del risultato + implicazioni terapeutiche (100-150 parole)"
  }}
]

Esempi: GFR (CKD-EPI), BMI, score CURB-65, CHA2DS2-VASc, APACHE II, SOFA, Child-Pugh, MELD, Glasgow, ecc.
Genera 10 calcoli clinici."""
    
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
    
    def format_for_training(self, calc: dict, specialty: str) -> dict:
        return {
            "messages": [
                {"role": "system", "content": "Sei ALL1E TUTOR MEDICINA per calcoli clinici."},
                {"role": "user", "content": calc['request']},
                {"role": "assistant", "content": f"{calc['calculation']}\n\n{calc['interpretation']}"}
            ],
            "metadata": {
                "type": "medicina_function_calling",
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
            response = self.client.generate(messages, temperature=0.7, max_tokens=6000)
            calc_list = self.parse_response(response)
            return [self.format_for_training(c, specialty) for c in calc_list if 'request' in c and 'calculation' in c]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate_all(self, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} medicina function calling\n{'='*80}")
        data = prepare_for_generation()
        chunks = data['chunks']
        all_calcs = []
        
        for chunk in tqdm(chunks, desc="  Medicina Function"):
            if len(all_calcs) >= target:
                break
            specialty = chunk.get('specialty', 'medicina')
            batch = self.generate_batch(chunk['text'], specialty)
            all_calcs.extend(batch)
            if len(all_calcs) % 100 == 0:
                with open(output_path, 'w', encoding='utf-8') as f:
                    for c in all_calcs:
                        f.write(json.dumps(c, ensure_ascii=False) + '\n')
                print(f"   💾 Saved {len(all_calcs)}")
            time.sleep(0.1)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for c in all_calcs[:target]:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
        print(f"\n✅ Generated {len(all_calcs[:target])} function calling")
        return all_calcs[:target]

def main():
    print("="*80 + "\n🚀 MEDICINA FUNCTION CALLING GENERATOR\n" + "="*80)
    generator = FunctionMedicinaGenerator()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2.1_generation/output"
    generator.generate_all(4000, f"{output_dir}/function_medicina.jsonl")
    print("\n✅ FUNCTION CALLING GENERATION COMPLETE")

if __name__ == "__main__":
    main()
