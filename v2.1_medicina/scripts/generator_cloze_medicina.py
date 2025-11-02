"""
CLOZE Generator MEDICINA - Terminologia medica con [BLANK]
Target: 8,000 esempi da 26 libri Secrets/WAU
"""
import json, time
from openrouter_client import OpenRouterClient
from load_secrets_books import prepare_for_generation
from tqdm import tqdm
import re

class ClozeMedicinaGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, chunk: str, specialty: str) -> str:
        return f"""Genera 10 cloze test di terminologia medica su {specialty.upper()}.

CONTENUTO CLINICO:
{chunk[:3000]}

OUTPUT (JSON array):
[
  {{
    "sentence": "Frase con [BLANK] che rimuove termine medico chiave",
    "correct_word": "termine medico corretto",
    "explanation": "Spiegazione del termine + contesto clinico + quando si usa (100-150 parole)"
  }}
]

Genera 10 cloze test su termini medici chiave."""
    
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
    
    def format_for_training(self, cloze: dict, specialty: str) -> dict:
        return {
            "messages": [
                {"role": "system", "content": "Sei ALL1E TUTOR MEDICINA per terminologia."},
                {"role": "user", "content": f"Completa: {cloze['sentence']}"},
                {"role": "assistant", "content": f"La parola corretta è: {cloze['correct_word']}\n\n{cloze['explanation']}"}
            ],
            "metadata": {
                "type": "medicina_cloze_terminology",
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
            cloze_list = self.parse_response(response)
            return [self.format_for_training(c, specialty) for c in cloze_list if 'sentence' in c and 'correct_word' in c]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate_all(self, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} medicina cloze\n{'='*80}")
        data = prepare_for_generation()
        chunks = data['chunks']
        all_cloze = []
        
        for chunk in tqdm(chunks, desc="  Medicina Cloze"):
            if len(all_cloze) >= target:
                break
            specialty = chunk.get('specialty', 'medicina')
            batch = self.generate_batch(chunk['text'], specialty)
            all_cloze.extend(batch)
            if len(all_cloze) % 100 == 0:
                with open(output_path, 'w', encoding='utf-8') as f:
                    for c in all_cloze:
                        f.write(json.dumps(c, ensure_ascii=False) + '\n')
                print(f"   💾 Saved {len(all_cloze)}")
            time.sleep(0.1)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for c in all_cloze[:target]:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
        print(f"\n✅ Generated {len(all_cloze[:target])} cloze")
        return all_cloze[:target]

def main():
    print("="*80 + "\n🚀 MEDICINA CLOZE GENERATOR\n" + "="*80)
    generator = ClozeMedicinaGenerator()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2.1_generation/output"
    generator.generate_all(8000, f"{output_dir}/cloze_medicina.jsonl")
    print("\n✅ CLOZE GENERATION COMPLETE")

if __name__ == "__main__":
    main()
