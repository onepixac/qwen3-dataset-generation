"""CLOZE Generator - Con evaluation_explanation pedagogica"""
import json, time
from openrouter_client import OpenRouterClient
from load_simone_books import load_simone_textbooks, chunk_text
from tqdm import tqdm

class ClozeGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, chunk: str, subject: str) -> str:
        return f"""Sei un esperto nella creazione di cloze test educativi in italiano.

Genera 5 cloze test dal seguente testo di {subject.upper()}:

{chunk[:2000]}

REGOLE:
1. [BLANK] rimuove UNA SOLA parola chiave importante
2. Parola deducibile dal contesto
3. Preferisci: sostantivi tecnici, verbi d'azione, concetti chiave
4. EVITA: articoli, preposizioni, congiunzioni

OUTPUT (JSON array):
[
  {{
    "sentence": "Testo con [BLANK]...",
    "correct_word": "parola",
    "explanation_markdown": "Breve spiegazione (2-3 righe)",
    "evaluation_explanation": "Spiegazione pedagogica dettagliata: perché questa parola è corretta, come si deduce dal contesto, applicazioni pratiche, domande socratiche (5-10 righe)"
  }}
]

Genera 5 cloze test."""
    
    def parse_response(self, response: str):
        import re
        try:
            if response.strip().startswith('['):
                return json.loads(response)
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return []
        except:
            return []
    
    def format_for_training(self, cloze: dict, subject: str) -> dict:
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "Sei un esperto nella creazione di cloze test educativi in italiano."
                },
                {
                    "role": "user",
                    "content": f"Genera un cloze test da questo testo:\n\n{cloze.get('context', 'Testo educativo')}"
                },
                {
                    "role": "assistant",
                    "content": json.dumps({
                        "sentence": cloze['sentence'],
                        "correct_word": cloze['correct_word'],
                        "explanation_markdown": cloze['explanation_markdown'],
                        "difficulty": "medio"
                    }, ensure_ascii=False)
                }
            ],
            "cloze_data": {
                "evaluation_explanation": cloze['evaluation_explanation']
            },
            "metadata": {
                "type": "cloze",
                "subject": subject,
                "source": "simone_textbooks"
            }
        }
    
    def generate_batch(self, chunk: str, subject: str):
        prompt = self.create_prompt(chunk, subject)
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.generate(messages, temperature=0.7, max_tokens=4000)
            cloze_list = self.parse_response(response)
            return [self.format_for_training(c, subject) for c in cloze_list if all(k in c for k in ['sentence', 'correct_word', 'explanation_markdown', 'evaluation_explanation'])]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate_for_subject(self, books, subject: str, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} cloze for: {subject.upper()}\n{'='*80}")
        all_cloze = []
        
        for book in books:
            print(f"\n📚 Book: {book['file_title']}")
            chunks = chunk_text(book['text'], 2000)
            needed = (target - len(all_cloze)) // 5 + 1
            
            for chunk in tqdm(chunks[:needed], desc="  Generating"):
                if len(all_cloze) >= target:
                    break
                batch = self.generate_batch(chunk, subject)
                all_cloze.extend(batch)
                if len(all_cloze) % 50 == 0:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for c in all_cloze:
                            f.write(json.dumps(c, ensure_ascii=False) + '\n')
                    print(f"   💾 Saved {len(all_cloze)}")
                time.sleep(0.1)  # Optimized
            
            if len(all_cloze) >= target:
                break
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for c in all_cloze[:target]:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Generated {len(all_cloze[:target])} cloze")
        return all_cloze[:target]

def main():
    print("="*80 + "\n🚀 CLOZE GENERATOR\n" + "="*80)
    generator = ClozeGenerator()
    categories = load_simone_textbooks()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2_dataset_generation/output"
    
    targets = {"diritto": 5000, "economia": 3000, "cultura_generale": 2000}
    
    for subject, count in targets.items():
        if categories.get(subject):
            output = f"{output_dir}/cloze_{subject}.jsonl"
            generator.generate_for_subject(categories[subject], subject, count, output)
    
    print("\n✅ CLOZE GENERATION COMPLETE")

if __name__ == "__main__":
    main()
