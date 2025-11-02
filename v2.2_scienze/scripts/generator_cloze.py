"""Cloze Generator v2.2 SCIENZE - LEVEL 9: 180 concurrent"""
import json, argparse
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
from openrouter_client import OpenRouterClient

class ClozeGenerator:
    def __init__(self, materia: str, target: int):
        self.materia, self.target = materia, target
        self.base_dir = Path(__file__).parent
        self.output_file = self.base_dir / "output" / f"{materia}_cloze.jsonl"
        self.checkpoint_file = self.base_dir / "checkpoints" / f"{materia}_cloze_checkpoint.json"
        self.chunks_file = self.base_dir / "checkpoints" / f"{materia}_chunks.json"
        self.client = OpenRouterClient()
        self.completed = 0
        self.max_concurrent = 180
    
    def load_chunks(self):
        with open(self.chunks_file, encoding="utf-8") as f:
            return json.load(f)
    
    def load_checkpoint(self):
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                return json.load(f).get("last_chunk_idx", 0)
        return 0
    
    def save_checkpoint(self, idx, count):
        with open(self.checkpoint_file, "w") as f:
            json.dump({"last_chunk_idx": idx, "examples_completed": count}, f)
    
    def create_prompt(self, text):
        return f"""Genera 2 cloze test da: {text[:2000]}\nJSON: [{{"sentence": "Testo con [BLANK]", "answer": "parola", "explanation": "Perché 100 parole"}}]"""
    
    def generate_batch(self, chunks, start, end):
        results = []
        for idx in range(start, min(end, len(chunks))):
            try:
                text = chunks[idx].get("text", "")
                if not text: continue
                data = self.client.generate_json(self.create_prompt(text), max_retries=3)
                for item in data:
                    if "sentence" in item:
                        results.append({"messages": [{"role": "user", "content": item["sentence"]}, {"role": "assistant", "content": f"{item['answer']}\n\n{item.get('explanation', '')}"}], "metadata": {"domain": self.materia, "task_type": "cloze"}})
            except: pass
        return results
    
    def run(self):
        print(f"\n📝 CLOZE - {self.materia.upper()}, Target: {self.target}")
        chunks = self.load_chunks()
        start_idx = self.load_checkpoint()
        pbar = tqdm(total=self.target, initial=self.completed)
        idx = start_idx
        while self.completed < self.target and idx < len(chunks):
            batch_end = min(idx + 50, len(chunks))
            examples = asyncio.run(self.generate_batch(chunks, idx, batch_end))
            if examples:
                with open(self.output_file, "a", encoding="utf-8") as f:
                    for ex in examples:
                        f.write(json.dumps(ex, ensure_ascii=False) + "\n")
                self.completed += len(examples)
                pbar.update(len(examples))
            if self.completed % 50 == 0:
                self.save_checkpoint(idx, self.completed)
            idx = batch_end
        pbar.close()
        self.save_checkpoint(idx, self.completed)
        print(f"✅ DONE: {self.completed}/{self.target}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--materia", required=True)
    parser.add_argument("--target", type=int, required=True)
    args = parser.parse_args()
    ClozeGenerator(args.materia, args.target).run()
