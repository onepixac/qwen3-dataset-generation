"""
Quiz Generator for v2.2 SCIENZE - LEVEL 9: 200 concurrent
Based on generator_chat.py with quiz-specific prompts
"""
import json, argparse
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
from openrouter_client import OpenRouterClient

class QuizGenerator:
    def __init__(self, materia: str, target: int):
        self.materia = materia
        self.target = target
        self.base_dir = Path(__file__).parent
        self.output_file = self.base_dir / "output" / f"{materia}_quiz.jsonl"
        self.checkpoint_file = self.base_dir / "checkpoints" / f"{materia}_quiz_checkpoint.json"
        self.chunks_file = self.base_dir / "checkpoints" / f"{materia}_chunks.json"
        self.client = OpenRouterClient()
        self.completed = 0
        self.max_concurrent = 200  # LEVEL 9
    
    def load_chunks(self) -> List[Dict]:
        with open(self.chunks_file, encoding="utf-8") as f:
            return json.load(f)
    
    def load_checkpoint(self) -> int:
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                return json.load(f).get("last_chunk_idx", 0)
        return 0
    
    def save_checkpoint(self, chunk_idx: int, examples_count: int):
        with open(self.checkpoint_file, "w") as f:
            json.dump({"last_chunk_idx": chunk_idx, "examples_completed": examples_count}, f)
    
    def create_prompt(self, chunk_text: str) -> str:
        return f"""Sei esperto di {self.materia}. Genera 3 quiz educativi da questo testo:

{chunk_text[:2500]}

OUTPUT JSON:
[{{"question": "Domanda chiara", "options": ["A", "B", "C", "D", "E"], "correct": 0-4, "explanation": "Spiegazione 150 parole"}}]

Qualità alta, distractors plausibili."""
    
    def generate_batch(self, chunks: List[Dict], start_idx: int, end_idx: int) -> List[Dict]:
        results = []
        for idx in range(start_idx, min(end_idx, len(chunks))):
            try:
                chunk_text = chunks[idx].get("text", "") or chunks[idx].get("chunk_text", "")
                if not chunk_text:
                    continue
                
                quiz_data = self.client.generate_json(self.create_prompt(chunk_text), max_retries=3)
                
                for quiz in quiz_data:
                    if "question" in quiz and "options" in quiz:
                        results.append({
                            "messages": [
                                {"role": "user", "content": quiz["question"]},
                                {"role": "assistant", "content": f"Risposta corretta: {quiz['options'][quiz['correct']]}\\n\\n{quiz.get('explanation', '')}"}
                            ],
                            "metadata": {"domain": self.materia, "task_type": "quiz", "generation": "v2.2"}
                        })
            except Exception as e:
                print(f"   ⚠️ Error chunk {idx}: {e}")
        return results
    
    def save_batch(self, examples: List[Dict]):
        with open(self.output_file, "a", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        self.completed += len(examples)
    
    def run(self):
        print(f"\n❓ QUIZ GENERATOR - {self.materia.upper()}")
        print(f"   Target: {self.target}, Max concurrent: {self.max_concurrent}")
        
        chunks = self.load_chunks()
        start_idx = self.load_checkpoint()
        
        pbar = tqdm(total=self.target, initial=self.completed, desc=f"   {self.materia} Quiz")
        
        chunk_idx = start_idx % len(chunks) if len(chunks) > 0 else 0
        while self.completed < self.target:
            batch_end = min(chunk_idx + 50, len(chunks))
            examples = asyncio.run(self.generate_batch(chunks, chunk_idx, batch_end))
            
            if examples:
                self.save_batch(examples)
                pbar.update(len(examples))
            
            if self.completed % 50 == 0:
                self.save_checkpoint(chunk_idx, self.completed)
            
            chunk_idx = batch_end % len(chunks) if len(chunks) > 0 else 0
        
        pbar.close()
        self.save_checkpoint(chunk_idx, self.completed)
        print(f"\n✅ COMPLETED: {self.completed}/{self.target}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--materia", required=True)
    parser.add_argument("--target", type=int, required=True)
    args = parser.parse_args()
    QuizGenerator(args.materia, args.target).run()
