"""
CITATIONS Generator MEDICINA - Risposte con citazioni [1][2][3]
Target: 6,000 esempi da 26 libri Secrets/WAU
"""
import json, time
from openrouter_client import OpenRouterClient
from load_secrets_books import prepare_for_generation
from tqdm import tqdm
import re

class CitationsMedicinaGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, chunk: str, specialty: str) -> str:
        return f"""Genera 10 Q&A con citazioni testuali su {specialty.upper()}.

CONTENUTO CLINICO:
{chunk[:3000]}

OUTPUT (JSON array):
[
  {{
    "question": "Domanda clinica che richiede riferimenti precisi al testo",
    "answer": "Risposta con citazioni [1], [2], [3] che fanno riferimento al testo fonte. Usa le citazioni per supportare le affermazioni cliniche. (150-200 parole)"
  }}
]

IMPORTANTE: Usa [1], [2], [3] per citare parti specifiche del testo.
Genera 10 Q&A con citazioni."""
    
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
    
    def format_for_training(self, qa: dict, specialty: str) -> dict:
        return {
            "messages": [
                {"role": "system", "content": "Sei ALL1E TUTOR MEDICINA con citazioni precise."},
                {"role": "user", "content": qa['question']},
                {"role": "assistant", "content": qa['answer']}
            ],
            "metadata": {
                "type": "medicina_citations",
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
            response = self.client.generate(messages, temperature=0.7, max_tokens=8000)
            qa_list = self.parse_response(response)
            return [self.format_for_training(q, specialty) for q in qa_list if 'question' in q and 'answer' in q]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate_all(self, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} medicina citations\n{'='*80}")
        data = prepare_for_generation()
        chunks = data['chunks']
        all_qa = []
        
        for chunk in tqdm(chunks, desc="  Medicina Citations"):
            if len(all_qa) >= target:
                break
            specialty = chunk.get('specialty', 'medicina')
            batch = self.generate_batch(chunk['text'], specialty)
            all_qa.extend(batch)
            if len(all_qa) % 100 == 0:
                with open(output_path, 'w', encoding='utf-8') as f:
                    for q in all_qa:
                        f.write(json.dumps(q, ensure_ascii=False) + '\n')
                print(f"   💾 Saved {len(all_qa)}")
            time.sleep(0.1)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for q in all_qa[:target]:
                f.write(json.dumps(q, ensure_ascii=False) + '\n')
        print(f"\n✅ Generated {len(all_qa[:target])} citations")
        return all_qa[:target]

def main():
    print("="*80 + "\n🚀 MEDICINA CITATIONS GENERATOR\n" + "="*80)
    generator = CitationsMedicinaGenerator()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2.1_generation/output"
    generator.generate_all(6000, f"{output_dir}/citations_medicina.jsonl")
    print("\n✅ CITATIONS GENERATION COMPLETE")

if __name__ == "__main__":
    main()
