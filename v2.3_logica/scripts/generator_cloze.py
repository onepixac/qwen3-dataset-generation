"""
Chat RAG Generator for v2.2 SCIENZE
LEVEL 9 Optimizations: 200 concurrent, checkpoint support
"""
import json
import argparse
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict
from tqdm.asyncio import tqdm
from openrouter_client import OpenRouterClient

class ChatGenerator:
    """
    Generates cloze RAG conversations from scientific textbook chunks
    
    LEVEL 9 Optimizations:
    - 200 concurrent requests
    - Checkpoint every 50 examples
    - Auto-resume from last checkpoint
    - Progress tracking with tqdm
    """
    
    def __init__(self, materia: str, target: int):
        self.materia = materia
        self.target = target
        self.base_dir = Path(__file__).parent
        self.output_file = self.base_dir / "output" / f"{materia}_cloze.jsonl"
        self.checkpoint_file = self.base_dir / "checkpoints" / f"{materia}_cloze_checkpoint.json"
        self.chunks_file = self.base_dir / "checkpoints" / f"{materia}_chunks.json"
        
        self.client = OpenRouterClient()
        self.completed = 0
        self.batch_size = 5  # FIXED: Sequential API calls, not concurrent
        self.max_concurrent = 200  # Not used (client is synchronous)
        
    def load_chunks(self) -> List[Dict]:
        """Load pre-categorized chunks for this materia"""
        if not self.chunks_file.exists():
            raise FileNotFoundError(f"Chunks file not found: {self.chunks_file}")
        
        with open(self.chunks_file, encoding="utf-8") as f:
            chunks = json.load(f)
        
        print(f"📚 Loaded {len(chunks)} chunks for {self.materia}")
        return chunks
    
    def load_checkpoint(self) -> int:
        """Load last completed chunk index"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                state = json.load(f)
            return state.get("last_chunk_idx", 0)
        return 0
    
    def save_checkpoint(self, chunk_idx: int, examples_count: int):
        """Save progress checkpoint"""
        state = {
            "materia": self.materia,
            "last_chunk_idx": chunk_idx,
            "examples_completed": examples_count,
            "target": self.target
        }
        with open(self.checkpoint_file, "w") as f:
            json.dump(state, f, indent=2)
    
    def create_prompt(self, chunk_text: str, chunk_index: int) -> str:
        """Create cloze generation prompt"""
        domain_context = {
            "biologia": "biologia cellulare, molecolare, anatomia e fisiologia",
            "chimica": "chimica generale, organica, inorganica e biochimica",
            "matematica_fisica": "matematica, fisica, calcolo e problem solving",
            "logica": "logica matematica, ragionamento e argomentazione",
            "cultura_generale": "cultura generale italiana, storia, geografia e società",
            "economia": "economia, diritto commerciale e diritto del lavoro"
        }
        
        context = domain_context.get(self.materia, "scienze")
        
        return f"""Sei un esperto educativo in {context} italiana.

Genera 12 conversazioni educative Q&A basate su questo chunk di testo:

---
{chunk_text[:3000]}
---

OUTPUT (JSON array):
[
  {{
    "question": "Domanda pedagogica (cosa, perché, come, quando si applica)",
    "answer": "Risposta educativa ECCELLENTE che:\\n1. Risponde direttamente alla domanda\\n2. Spiega concetti con chiarezza\\n3. Include esempi pratici\\n4. Aggiunge 1-2 domande socratiche\\n5. Tono incoraggiante e pedagogico\\n6. Lunghezza: 200-250 parole"
  }}
]

IMPORTANTE:
- 12 Q&A diverse per questo chunk
- Qualità > quantità
- Focus su comprensione profonda
- Tono professionale ma accessibile
"""
    
    async def generate_batch(self, chunks: List[Dict], start_idx: int, end_idx: int) -> List[Dict]:
        """Generate cloze examples for a batch of chunks"""
        results = []
        batch_results = []
        
        # Process chunks sequentially (client is synchronous)
        for idx in range(start_idx, min(end_idx, len(chunks))):
            chunk = chunks[idx]
            chunk_text = chunk.get("text", "") or chunk.get("chunk_text", "")
            
            if not chunk_text:
                batch_results.append([])
                continue
            
            try:
                prompt = self.create_prompt(chunk_text, idx)
                result = self.client.generate_json(prompt, max_retries=3)
                batch_results.append(result)
            except Exception as e:
                print(f"   ❌ Error on chunk {idx}: {e}")
                batch_results.append([])
        
        # Flatten results
        for chunk_result in batch_results:
            if isinstance(chunk_result, list):
                for item in chunk_result:
                    if "question" in item and "answer" in item:
                        results.append({
                            "messages": [
                                {"role": "user", "content": item["question"]},
                                {"role": "assistant", "content": item["answer"]}
                            ],
                            "metadata": {
                                "domain": self.materia,
                                "task_type": "cloze_rag",
                                "generation": "v2.3_cultura"
                            }
                        })
        
        return results
    
    def save_batch(self, examples: List[Dict]):
        """Append examples to output file"""
        with open(self.output_file, "a", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        self.completed += len(examples)
    
    def run(self):
        """Main generation loop"""
        print(f"\n💬 CLOZE GENERATOR - {self.materia.upper()}")
        print(f"   Target: {self.target} examples")
        print(f"   Batch size: {self.batch_size}")
        print(f"   Max concurrent: {self.max_concurrent}")
        
        # Load chunks
        chunks = self.load_chunks()
        
        # Load checkpoint
        start_idx = self.load_checkpoint()
        print(f"   Resuming from chunk {start_idx}/{len(chunks)}")
        
        # Calculate examples per chunk
        examples_per_chunk = self.target // len(chunks)
        print(f"   ~{examples_per_chunk} examples per chunk")
        
        # Generation loop
        pbar = tqdm(total=self.target, initial=self.completed, desc=f"   {self.materia} Chat")
        
        chunk_idx = start_idx % len(chunks) if len(chunks) > 0 else 0
        while self.completed < self.target:
            # Process batch
            batch_end = min(chunk_idx + self.batch_size, len(chunks))
            
            try:
                examples = asyncio.run(self.generate_batch(chunks, chunk_idx, batch_end))
                
                if examples:
                    self.save_batch(examples)
                    pbar.update(len(examples))
                
                # Checkpoint every 50 examples
                if self.completed % 50 == 0:
                    self.save_checkpoint(chunk_idx, self.completed)
                
                chunk_idx = batch_end % len(chunks) if len(chunks) > 0 else 0
                
            except KeyboardInterrupt:
                print(f"\n⚠️  Interrupted at chunk {chunk_idx}")
                self.save_checkpoint(chunk_idx, self.completed)
                break
            except Exception as e:
                print(f"\n❌ Error at chunk {chunk_idx}: {e}")
                self.save_checkpoint(chunk_idx, self.completed)
                chunk_idx += 1  # Skip problematic chunk
        
        pbar.close()
        
        # Final checkpoint
        self.save_checkpoint(chunk_idx, self.completed)
        
        print(f"\n✅ COMPLETED: {self.completed}/{self.target} examples")
        print(f"   Output: {self.output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--materia", required=True)
    parser.add_argument("--target", type=int, required=True)
    args = parser.parse_args()
    
    generator = ChatGenerator(args.materia, args.target)
    generator.run()
