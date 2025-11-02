"""CITATIONS Generator - RAG con sources [1][2][3]"""
import json, time
from openrouter_client import OpenRouterClient
from load_simone_books import load_simone_textbooks, chunk_text
from tqdm import tqdm

class CitationsGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, chunks: list, subject: str) -> str:
        sources_text = "\n\n".join([f"[SOURCE {i+1}]\n{c[:800]}" for i, c in enumerate(chunks[:5])])
        
        return f"""Sei ALL1E TUTOR, assistente educativo esperto.

Genera 5 conversazioni educative su {subject.upper()} con citations [1][2][3].

SOURCES DISPONIBILI:
{sources_text}

OUTPUT (JSON):
[
  {{
    "question": "Domanda educativa complessa che richiede multiple sources",
    "answer": "Risposta dettagliata con citations [1][2][3] integrate nel testo. La risposta deve:\n- Spiegare concetti con citazioni appropriate\n- Usare [1][2][3] nel punto esatto dove serve il source\n- Concludere con 2-3 domande socratiche\n- Essere pedagogica e incoraggiante",
    "sources": [
      {{"citation": "[1]", "text": "Estratto breve (max 200 parole) dal SOURCE 1"}},
      {{"citation": "[2]", "text": "Estratto breve dal SOURCE 2"}},
      {{"citation": "[3]", "text": "Estratto breve dal SOURCE 3"}}
    ]
  }}
]

REGOLE:
1. Answer usa [1][2][3] integrate naturalmente
2. Sources contiene SOLO gli estratti citati
3. Tono: pedagogico, con domande socratiche
4. Basati SOLO sui sources forniti

Genera 5 conversazioni."""
    
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
    
    def format_for_training(self, citation: dict, subject: str) -> dict:
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "Sei ALL1E TUTOR, assistente educativo con citations."
                },
                {
                    "role": "user",
                    "content": citation['question']
                },
                {
                    "role": "assistant",
                    "content": citation['answer']
                }
            ],
            "sources": citation['sources'],
            "metadata": {
                "type": "citations",
                "topic": subject,
                "source": "simone_textbooks"
            }
        }
    
    def generate_batch(self, chunks: list, subject: str):
        prompt = self.create_prompt(chunks, subject)
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.generate(messages, temperature=0.7, max_tokens=6000)
            citations_list = self.parse_response(response)
            return [self.format_for_training(c, subject) for c in citations_list if all(k in c for k in ['question', 'answer', 'sources'])]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate_for_subject(self, books, subject: str, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} citations for: {subject.upper()}\n{'='*80}")
        all_citations = []
        
        for book in books:
            print(f"\n📚 Book: {book['file_title']}")
            all_chunks = chunk_text(book['text'], 1000)
            
            # Group chunks in sets of 5
            for i in tqdm(range(0, len(all_chunks), 5), desc="  Generating"):
                if len(all_citations) >= target:
                    break
                
                chunk_set = all_chunks[i:i+5]
                if len(chunk_set) < 3:
                    continue
                
                batch = self.generate_batch(chunk_set, subject)
                all_citations.extend(batch)
                
                if len(all_citations) % 50 == 0:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for c in all_citations:
                            f.write(json.dumps(c, ensure_ascii=False) + '\n')
                    print(f"   💾 Saved {len(all_citations)}")
                time.sleep(0.1)  # Optimized
            
            if len(all_citations) >= target:
                break
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for c in all_citations[:target]:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Generated {len(all_citations[:target])} citations")
        return all_citations[:target]

def main():
    print("="*80 + "\n🚀 CITATIONS GENERATOR\n" + "="*80)
    generator = CitationsGenerator()
    categories = load_simone_textbooks()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2_dataset_generation/output"
    
    targets = {"diritto": 6000, "economia": 4000}
    
    for subject, count in targets.items():
        if categories.get(subject):
            output = f"{output_dir}/citations_{subject}.jsonl"
            generator.generate_for_subject(categories[subject], subject, count, output)
    
    print("\n✅ CITATIONS GENERATION COMPLETE")

if __name__ == "__main__":
    main()
