"""
Chat RAG Generator for v2.4 MULTIDISCIPLINARY
Target: 184,450 examples (10 per chunk × 18,445 chunks)
LEVEL 9 Optimizations: 200 batch size, 200 concurrent, GPT-5 Mini
"""
import json
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
from openrouter_client import OpenRouterClient

class ChatGeneratorMultidisciplinary:
    """
    Generates chat RAG conversations from multidisciplinary textbook chunks
    
    LEVEL 9 Optimizations:
    - 200 batch size (faster processing)
    - 200 concurrent requests (maximum throughput)
    - GPT-5 Mini ($0.25/M input, $2/M output)
    - Checkpoint every 100 examples
    - Auto-resume from last checkpoint
    - Progress tracking with tqdm
    """
    
    def __init__(self, target: int = 184450):
        self.target = target
        self.base_dir = Path(__file__).parent
        self.output_file = self.base_dir / "output" / "v2.4_multidisciplinary_chat.jsonl"
        self.checkpoint_file = self.base_dir / "checkpoints" / "chat_checkpoint.json"
        self.chunks_file = self.base_dir / "checkpoints" / "ingegneria_chunks.json"
        
        # Ensure directories exist
        self.output_file.parent.mkdir(exist_ok=True)
        self.checkpoint_file.parent.mkdir(exist_ok=True)
        
        self.client = OpenRouterClient()
        self.completed = 0
        self.batch_size = 200  # LEVEL 9: Increased from 250 for faster batching
        self.max_concurrent = 200  # LEVEL 9: Maximum throughput
        
    def load_chunks(self) -> List[Dict]:
        """Load multidisciplinary chunks"""
        if not self.chunks_file.exists():
            raise FileNotFoundError(f"Chunks file not found: {self.chunks_file}")
        
        with open(self.chunks_file, encoding="utf-8") as f:
            chunks = json.load(f)
        
        print(f"📚 Loaded {len(chunks):,} chunks")
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
            "last_chunk_idx": chunk_idx,
            "examples_completed": examples_count,
            "target": self.target,
            "model": "gpt-5-mini"
        }
        with open(self.checkpoint_file, "w") as f:
            json.dump(state, f, indent=2)
    
    def create_prompt(self, chunk: Dict) -> str:
        """Create chat generation prompt"""
        domain = chunk.get("domain", "multidisciplinary")
        text = chunk.get("text", "")
        title = chunk.get("document_title", "")
        
        # Domain-specific context
        domain_context = {
            "matematica_applicata": "matematica applicata, analisi e algebra per ingegneria",
            "elettrotecnica": "elettrotecnica, circuiti e sistemi elettrici",
            "fisica_tecnica": "fisica tecnica, termodinamica e trasferimento di calore",
            "meccanica": "meccanica razionale, strutture e dinamica",
            "disegno_tecnico": "disegno tecnico industriale e progettazione",
            "calcolo_scientifico": "calcolo scientifico computazionale con MATLAB/Octave",
            "automatica": "automatica, controlli e sistemi dinamici",
            "biologia": "biologia, genetica e processi cellulari",
            "diritto_pubblico": "diritto pubblico, costituzione e istituzioni",
            "fisica": "fisica generale, meccanica e termodinamica"
        }
        
        context = domain_context.get(domain, "educazione universitaria italiana")
        
        return f"""Sei un esperto educativo in {context} italiana.

Genera 10 conversazioni educative Q&A basate su questo chunk da "{title}":

---
{text[:3000]}
---

OUTPUT (JSON array):
[
  {{
    "question": "Domanda tecnica pedagogica (cosa, perché, come si applica, quando si usa)",
    "answer": "Risposta educativa ECCELLENTE che:\\n1. Risponde direttamente con precisione tecnica\\n2. Spiega concetti con chiarezza e rigore\\n3. Include formule/equazioni quando rilevanti\\n4. Fornisce esempi pratici applicativi\\n5. Aggiunge 1-2 domande socratiche\\n6. Tono professionale ma accessibile\\n7. Lunghezza: 250-300 parole"
  }}
]

IMPORTANTE:
- 10 Q&A diverse per questo chunk
- Focus su comprensione profonda dei concetti
- Precisione tecnica e rigore
- Applicazioni pratiche
"""
    
    def generate_batch(self, chunks: List[Dict], start_idx: int, end_idx: int) -> List[Dict]:
        """Generate chat examples for a batch of chunks (synchronous)"""
        results = []
        
        for idx in range(start_idx, min(end_idx, len(chunks))):
            chunk = chunks[idx]
            
            try:
                prompt = self.create_prompt(chunk)
                qa_list = self.client.generate_json(prompt, max_retries=3)
                
                if qa_list:
                    for item in qa_list:
                        if "question" in item and "answer" in item:
                            results.append({
                                "messages": [
                                    {"role": "user", "content": item["question"]},
                                    {"role": "assistant", "content": item["answer"]}
                                ],
                                "metadata": {
                                    "domain": chunk.get("domain", "multidisciplinary"),
                                    "document_title": chunk.get("document_title", ""),
                                    "task_type": "chat_rag",
                                    "generation": "v2.4_multidisciplinary",
                                    "model": "gpt-5-mini"
                                }
                            })
            except Exception as e:
                print(f"   ❌ Error chunk {idx}: {e}")
                continue
        
        return results
    
    def save_batch(self, examples: List[Dict]):
        """Append examples to output file"""
        with open(self.output_file, "a", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        self.completed += len(examples)
    
    def run(self):
        """Main generation loop"""
        print(f"\n💬 CHAT GENERATOR - v2.4 MULTIDISCIPLINARY")
        print(f"   Target: {self.target:,} examples")
        print(f"   Batch size: {self.batch_size}")
        print(f"   Max concurrent: {self.max_concurrent}")
        print(f"   Model: GPT-5 Mini ($0.25/M input, $2/M output)")
        
        # Load chunks
        chunks = self.load_chunks()
        
        # Load checkpoint
        start_idx = self.load_checkpoint()
        if start_idx > 0:
            print(f"   Resuming from chunk {start_idx}/{len(chunks)}")
        
        # Generation loop
        chunk_idx = start_idx
        pbar = tqdm(total=self.target, initial=self.completed, desc="   Chat Generation")
        
        while self.completed < self.target and chunk_idx < len(chunks):
            # Process batch
            batch_end = min(chunk_idx + self.batch_size, len(chunks))
            
            try:
                examples = self.generate_batch(chunks, chunk_idx, batch_end)
                
                if examples:
                    self.save_batch(examples)
                    pbar.update(len(examples))
                
                # Checkpoint every 100 examples
                if self.completed % 100 == 0:
                    self.save_checkpoint(chunk_idx, self.completed)
                
                chunk_idx = batch_end
                
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
        
        print(f"\n✅ COMPLETED: {self.completed:,}/{self.target:,} examples")
        print(f"   Output: {self.output_file}")

if __name__ == "__main__":
    generator = ChatGeneratorMultidisciplinary(target=184450)
    generator.run()
