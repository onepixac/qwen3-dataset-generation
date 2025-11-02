"""
QUIZ Generator MEDICINA - Quiz clinici con 5 opzioni
Target: 8,000 esempi da 26 libri Secrets/WAU
"""
import json, time
from openrouter_client import OpenRouterClient
from load_secrets_books import prepare_for_generation
from tqdm import tqdm
import re

class QuizMedicinaGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, chunk: str, specialty: str) -> str:
        return f"""Genera 10 quiz clinici ECCELLENTI con 5 opzioni su {specialty.upper()}.

CONTENUTO CLINICO:
{chunk[:3000]}

OUTPUT (JSON array):
[
  {{
    "question": "Domanda clinica che richiede ragionamento (NO mnemonica)",
    "options": ["1) opzione A", "2) opzione B", "3) opzione C", "4) opzione D", "5) opzione E"],
    "correct_answer": 1,
    "explanation": "Spiegazione: perché opzione 1 è corretta + perché le altre sono sbagliate + DD clinica (150-200 parole)"
  }}
]

Genera 10 quiz con 5 opzioni numerate 1-5."""
    
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
    
    def format_for_training(self, quiz: dict, specialty: str) -> dict:
        return {
            "messages": [
                {"role": "system", "content": "Sei ALL1E TUTOR MEDICINA per quiz clinici."},
                {"role": "user", "content": f"Quiz: {quiz['question']}\n\nOpzioni:\n" + "\n".join(quiz['options'])},
                {"role": "assistant", "content": f"Risposta corretta: {quiz['correct_answer']}\n\n{quiz['explanation']}"}
            ],
            "metadata": {
                "type": "medicina_quiz_clinical",
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
            quiz_list = self.parse_response(response)
            return [self.format_for_training(q, specialty) for q in quiz_list if 'question' in q and 'options' in q]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate_all(self, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} medicina quiz\n{'='*80}")
        data = prepare_for_generation()
        chunks = data['chunks']
        all_quizzes = []
        
        for chunk in tqdm(chunks, desc="  Medicina Quiz"):
            if len(all_quizzes) >= target:
                break
            specialty = chunk.get('specialty', 'medicina')
            batch = self.generate_batch(chunk['text'], specialty)
            all_quizzes.extend(batch)
            if len(all_quizzes) % 100 == 0:
                with open(output_path, 'w', encoding='utf-8') as f:
                    for q in all_quizzes:
                        f.write(json.dumps(q, ensure_ascii=False) + '\n')
                print(f"   💾 Saved {len(all_quizzes)}")
            time.sleep(0.1)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for q in all_quizzes[:target]:
                f.write(json.dumps(q, ensure_ascii=False) + '\n')
        print(f"\n✅ Generated {len(all_quizzes[:target])} quiz")
        return all_quizzes[:target]

def main():
    print("="*80 + "\n🚀 MEDICINA QUIZ GENERATOR\n" + "="*80)
    generator = QuizMedicinaGenerator()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2.1_generation/output"
    generator.generate_all(8000, f"{output_dir}/quiz_medicina.jsonl")
    print("\n✅ QUIZ GENERATION COMPLETE")

if __name__ == "__main__":
    main()
