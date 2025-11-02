"""
QUIZ Generator v2 - FORMATO CORRETTO
Genera quiz con explanations_markdown completo:
- Spiegazione pedagogica
- Analisi OGNI opzione (A, B, C, D, E)
- Sezione "Non Lo So"
- Domande socratiche
"""

import json
import time
from typing import List, Dict
from datasets import load_dataset
from openrouter_client import OpenRouterClient
from load_simone_books import load_simone_textbooks, chunk_text
from tqdm import tqdm

class QuizGeneratorV2:
    def __init__(self):
        self.client = OpenRouterClient()
        
        # Load medicina templates (5 best examples)
        ds = load_dataset("All1eOnepix/test-medicina-quiz-instruct", split="train")
        self.templates = [ds[i] for i in [0, 150, 500, 1000, 2500]]
    
    def create_quiz_prompt(self, chunk: str, subject: str) -> str:
        """Create prompt for quiz generation with FULL explanations"""
        
        # Format templates
        template_examples = ""
        for i, t in enumerate(self.templates[:3], 1):
            template_examples += f"\n=== ESEMPIO {i} ===\n{t['question']}\n\nSPIEGAZIONE:\n{t['answer']}\n"
        
        prompt = f"""Sei un esperto nella creazione di quiz educativi in italiano.

Hai questi 3 esempi GOLD STANDARD di quiz medicina:
{template_examples}

Ora genera 10 quiz di **{subject.upper()}** usando ESATTAMENTE lo stesso formato e stile.

CONTENUTO:
{chunk[:3500]}

FORMATO RICHIESTO (JSON):
[
  {{
    "question": "Domanda completa con contesto + 'Qual è/Quale/Come' + opzioni numerate 1) 2) 3) 4) 5)",
    "options": [
      {{"letter": "A", "text": "Opzione 1"}},
      {{"letter": "B", "text": "Opzione 2"}},
      {{"letter": "C", "text": "Opzione 3"}},
      {{"letter": "D", "text": "Opzione 4"}},
      {{"letter": "E", "text": "Opzione 5"}}
    ],
    "correct_answer": 2,
    "explanations": "Spiegazione: [Contesto pedagogico dettagliato]\\n\\nL'opzione A rappresenta...\\nL'opzione B...\\nL'opzione C (corretta) perché...\\nL'opzione D...\\nL'opzione E...\\n\\nNon Lo So: [Guida incoraggiante]\\n\\nDomande socratiche:\\n1. Come si applica...\\n2. Perché questo principio..."
  }}
]

REGOLE CRITICHE:
1. Question: Contesto + domanda + 5 opzioni numerate 1) 2) 3) 4) 5)
2. Options: Array con letters A-E
3. correct_answer: Indice 0-4
4. Explanations: COMPLETO con analisi OGNI opzione + "Non Lo So" + domande socratiche
5. Tono: Pedagogico, come esempi medicina
6. Basati SOLO sul contenuto fornito

Genera 10 quiz."""

        return prompt
    
    def parse_response(self, response: str) -> List[Dict]:
        """Parse GPT response"""
        try:
            # Try direct JSON
            if response.strip().startswith('['):
                return json.loads(response)
            
            # Extract from markdown
            import re
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            return []
        except:
            return []
    
    def format_for_training(self, quiz: Dict, subject: str) -> Dict:
        """Convert to training format"""
        
        # Build full question with options
        full_question = quiz['question'] + "\n\nOpzioni:\n"
        for opt in quiz['options']:
            full_question += f"{opt['letter']}) {opt['text']}\n"
        
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "Sei ALL1E TUTOR, assistente educativo esperto in quiz e spiegazioni."
                },
                {
                    "role": "user",
                    "content": full_question
                },
                {
                    "role": "assistant",
                    "content": quiz['explanations']
                }
            ],
            "quiz_data": {
                "options": [
                    {
                        "id": f"opt_{i}",
                        "letter": opt['letter'],
                        "is_correct": i == quiz['correct_answer'],
                        "option_text": opt['text']
                    }
                    for i, opt in enumerate(quiz['options'])
                ],
                "correct_answer": quiz['correct_answer']
            },
            "metadata": {
                "type": "quiz",
                "subject": subject,
                "source": "simone_textbooks",
                "generation": "openrouter_gpt4o_mini_v2"
            }
        }
    
    def generate_batch(self, chunk: str, subject: str) -> List[Dict]:
        """Generate batch of 10 quiz"""
        
        prompt = self.create_quiz_prompt(chunk, subject)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.generate(messages, temperature=0.7, max_tokens=8000)
            
            quiz_list = self.parse_response(response)
            
            if not quiz_list:
                return []
            
            formatted = []
            for quiz in quiz_list:
                if all(k in quiz for k in ['question', 'options', 'correct_answer', 'explanations']):
                    formatted.append(self.format_for_training(quiz, subject))
            
            return formatted
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []
    
    def generate_for_subject(self, books: List[Dict], subject: str, target: int, output_path: str):
        """Generate quiz for subject"""
        
        print(f"\n{'='*80}")
        print(f"📝 Generating {target} quiz for: {subject.upper()}")
        print(f"{'='*80}")
        
        all_quiz = []
        
        for book in books:
            print(f"\n📚 Book: {book['file_title']}")
            
            chunks = chunk_text(book['text'], chunk_size=3500)
            print(f"   Chunks: {len(chunks)}")
            
            needed = (target - len(all_quiz)) // 10 + 1
            
            for chunk in tqdm(chunks[:needed], desc="  Generating"):
                if len(all_quiz) >= target:
                    break
                
                batch = self.generate_batch(chunk, subject)
                all_quiz.extend(batch)
                
                # Save progress every 50
                if len(all_quiz) % 50 == 0:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for q in all_quiz:
                            f.write(json.dumps(q, ensure_ascii=False) + '\n')
                    print(f"   💾 Saved {len(all_quiz)}")
                
                time.sleep(0.1)  # Optimized rate limit (still respects 200 req/min)
            
            if len(all_quiz) >= target:
                break
        
        # Final save
        with open(output_path, 'w', encoding='utf-8') as f:
            for q in all_quiz[:target]:
                f.write(json.dumps(q, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Generated {len(all_quiz[:target])} quiz")
        return all_quiz[:target]

def main():
    print("="*80)
    print("🚀 QUIZ GENERATOR V2 - FORMATO CORRETTO")
    print("="*80)
    
    generator = QuizGeneratorV2()
    categories = load_simone_textbooks()
    
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2_dataset_generation/output"
    
    targets = {
        "diritto": 15000,
        "economia": 5000,
        "cultura_generale": 5000
    }
    
    for subject, count in targets.items():
        if categories.get(subject):
            output = f"{output_dir}/quiz_{subject}_v2.jsonl"
            generator.generate_for_subject(categories[subject], subject, count, output)
    
    print("\n✅ QUIZ GENERATION COMPLETE")

if __name__ == "__main__":
    main()
