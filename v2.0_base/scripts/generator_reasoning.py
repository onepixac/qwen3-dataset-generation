"""REASONING Generator - Con student_responses (correct/partial/incorrect)"""
import json, time
from openrouter_client import OpenRouterClient
from load_simone_books import load_simone_textbooks, chunk_text
from tqdm import tqdm

class ReasoningGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, chunk: str, subject: str) -> str:
        return f"""Sei un esperto educativo. Genera 3 domande di ragionamento critico su {subject.upper()}.

CONTENUTO:
{chunk[:2500]}

OUTPUT (JSON):
[
  {{
    "question": "## Domanda\\nCome/Perché/Quale [domanda che richiede ragionamento profondo]?",
    "domain": "{subject}",
    "difficulty": "medio",
    "key_concepts": ["concetto1", "concetto2", "concetto3"],
    "answer": "Risposta esperta di riferimento (10-15 righe con spiegazioni dettagliate, esempi pratici, domande socratiche)",
    "student_responses": [
      {{
        "type": "correct",
        "response": "Risposta corretta dello studente (realistica)",
        "feedback": "Feedback positivo pedagogico (5-8 righe): riconosce punti di forza, suggerisce approfondimenti, domande socratiche"
      }},
      {{
        "type": "partial",
        "response": "Risposta parzialmente corretta (realistica)",
        "feedback": "Feedback costruttivo (8-12 righe): evidenzia cosa è corretto, identifica lacune, pone domande socratiche per guidare, suggerisce approfondimenti"
      }},
      {{
        "type": "incorrect",
        "response": "Risposta errata (realistica)",
        "feedback": "Feedback correttivo pedagogico (10-15 righe): identifica misconcezioni, spiega l'errore con empatia, guida verso comprensione corretta con domande socratiche, suggerisce risorse"
      }}
    ]
  }}
]

Genera 3 domande di reasoning."""
    
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
    
    def format_for_training(self, reasoning: dict, subject: str) -> dict:
        return {
            "reasoning_question": reasoning,
            "metadata": {
                "type": "reasoning",
                "subject": subject,
                "source": "simone_textbooks"
            }
        }
    
    def generate_batch(self, chunk: str, subject: str):
        prompt = self.create_prompt(chunk, subject)
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.generate(messages, temperature=0.7, max_tokens=8000)
            reasoning_list = self.parse_response(response)
            return [self.format_for_training(r, subject) for r in reasoning_list if 'student_responses' in r and len(r['student_responses']) == 3]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate_for_subject(self, books, subject: str, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} reasoning for: {subject.upper()}\n{'='*80}")
        all_reasoning = []
        
        for book in books:
            print(f"\n📚 Book: {book['file_title']}")
            chunks = chunk_text(book['text'], 2500)
            needed = (target - len(all_reasoning)) // 3 + 1
            
            for chunk in tqdm(chunks[:needed], desc="  Generating"):
                if len(all_reasoning) >= target:
                    break
                batch = self.generate_batch(chunk, subject)
                all_reasoning.extend(batch)
                if len(all_reasoning) % 30 == 0:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for r in all_reasoning:
                            f.write(json.dumps(r, ensure_ascii=False) + '\n')
                    print(f"   💾 Saved {len(all_reasoning)}")
                time.sleep(0.1)  # Optimized
            
            if len(all_reasoning) >= target:
                break
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for r in all_reasoning[:target]:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Generated {len(all_reasoning[:target])} reasoning")
        return all_reasoning[:target]

def main():
    print("="*80 + "\n🚀 REASONING GENERATOR\n" + "="*80)
    generator = ReasoningGenerator()
    categories = load_simone_textbooks()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2_dataset_generation/output"
    
    targets = {"diritto": 5000, "economia": 3000, "cultura_generale": 2000}
    
    for subject, count in targets.items():
        if categories.get(subject):
            output = f"{output_dir}/reasoning_{subject}.jsonl"
            generator.generate_for_subject(categories[subject], subject, count, output)
    
    print("\n✅ REASONING GENERATION COMPLETE")

if __name__ == "__main__":
    main()
