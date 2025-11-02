"""
v2.8 Cinema & Media Studies - Chat/RAG Generator
Using GPT-4o-mini via OpenRouter for cost efficiency
"""

import asyncio
import json
import os
from datetime import datetime
from tqdm.asyncio import tqdm
from openrouter_client import OpenRouterClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", 45))
BATCH_DELAY_MS = int(os.getenv("BATCH_DELAY_MS", 500))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 150))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

# Topics for Cinema & Media Studies
TOPICS = {
    "linguaggio_cinematografico": {
        "count": 400,
        "seeds": [
            "Spiega il concetto di inquadratura e i suoi tipi (campo lungo, medio, primo piano)",
            "Come funziona il montaggio cinematografico?",
            "Qual è la differenza tra piano sequenza e montaggio parallelo?",
            "Spiega l'uso del colore nel cinema",
            "Come si crea la profondità di campo in una scena?"
        ]
    },
    "storia_cinema": {
        "count": 400,
        "seeds": [
            "Cos'è il neorealismo italiano? Esempi di film",
            "Spiega la nouvelle vague francese",
            "Come è nato il cinema sonoro?",
            "Qual è l'importanza di Fellini per il cinema italiano?",
            "Cos'è l'espressionismo tedesco?"
        ]
    },
    "analisi_narrativa": {
        "count": 300,
        "seeds": [
            "Come si analizza la struttura narrativa di un film?",
            "Spiega il concept di arco di trasformazione del personaggio",
            "Cosa sono i plot points in una sceneggiatura?",
            "Come funziona il flashback nel racconto cinematografico?",
            "Spiega la differenza tra storia e trama"
        ]
    },
    "generi_cinematografici": {
        "count": 300,
        "seeds": [
            "Quali sono le caratteristiche del film noir?",
            "Cos'è un western? Evoluzione del genere",
            "Spiega il thriller psicologico",
            "Come funziona la commedia italiana?",
            "Cosa distingue un film d'autore?"
        ]
    },
    "registi_autori": {
        "count": 300,
        "seeds": [
            "Qual è lo stile registico di Fellini?",
            "Spiega il cinema di Rossellini",
            "Come lavora Visconti con gli attori?",
            "Qual è la poetica di Antonioni?",
            "Spiega il cinema di Pasolini"
        ]
    },
    "sociologia_comunicazione": {
        "count": 200,
        "seeds": [
            "Spiega le teorie della comunicazione di massa",
            "Come funzionano gli effetti dei media sul pubblico?",
            "Cos'è l'agenda setting?",
            "Spiega la teoria degli usi e gratificazioni",
            "Come i social media hanno cambiato la comunicazione?"
        ]
    },
    "linguistica_cognitiva": {
        "count": 100,
        "seeds": [
            "Cosa sono le metafore concettuali secondo Lakoff?",
            "Come funziona il pensiero metaforico?",
            "Spiega la semantica cognitiva",
            "Quali sono le metafore di orientamento?",
            "Come il linguaggio plasma il pensiero?"
        ]
    }
}

# System prompt
SYSTEM_PROMPT = """Sei ALL1E TUTOR, assistente educativo italiano esperto in Cinema e Media Studies.

La tua expertise comprende:
- Storia del cinema (italiano e internazionale)
- Linguaggio cinematografico (inquadrature, montaggio, colore, suono)
- Analisi narrativa e visuale
- Generi cinematografici
- Registi e autori
- Sociologia della comunicazione
- Linguistica cognitiva

Rispondi SEMPRE in italiano con:
✅ Spiegazioni chiare e pedagogicamente efficaci
✅ Esempi concreti da film famosi
✅ Riferimenti a registi e opere
✅ Domande socratiche per stimolare il pensiero critico
✅ Connessioni interdisciplinari (cinema-società-linguaggio)

Formato richiesto: JSON con struttura:
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}

Rispondi SOLO con JSON valido, senza markdown o spiegazioni extra."""

class CinemaMediaChatGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self.generated_count = 0
        self.failed_count = 0
        
    async def generate_single(self, topic: str, seed: str, index: int) -> dict:
        """Generate single chat example"""
        async with self.semaphore:
            try:
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Topic: {topic}\n\nGenera una conversazione educativa basata su: {seed}\n\nLa conversazione deve essere naturale, pedagogica e includere domande socratiche."}
                ]
                
                response = await self.client.chat_completion_with_retry(
                    messages=messages,
                    max_retries=MAX_RETRIES
                )
                
                if not response:
                    return None
                
                # Parse JSON
                try:
                    # Remove markdown if present
                    if "```json" in response:
                        response = response.split("```json")[1].split("```")[0].strip()
                    elif "```" in response:
                        response = response.split("```")[1].split("```")[0].strip()
                    
                    data = json.loads(response)
                    
                    # Validate structure
                    if "messages" in data and len(data["messages"]) >= 2:
                        self.generated_count += 1
                        return data
                    else:
                        self.failed_count += 1
                        return None
                        
                except json.JSONDecodeError as e:
                    self.failed_count += 1
                    return None
                    
            except Exception as e:
                self.failed_count += 1
                return None
    
    async def generate_topic(self, topic: str, config: dict) -> list:
        """Generate all examples for a topic"""
        print(f"\n🎬 Generating {config['count']} examples for: {topic}")
        
        examples_per_seed = config['count'] // len(config['seeds'])
        tasks = []
        
        for seed in config['seeds']:
            for i in range(examples_per_seed):
                task = self.generate_single(topic, seed, i)
                tasks.append(task)
        
        # Generate with progress bar
        results = []
        for i in range(0, len(tasks), BATCH_SIZE):
            batch = tasks[i:i+BATCH_SIZE]
            batch_results = await tqdm.gather(*batch, desc=f"  {topic}")
            results.extend([r for r in batch_results if r is not None])
            
            # Batch delay
            if i + BATCH_SIZE < len(tasks):
                await asyncio.sleep(BATCH_DELAY_MS / 1000)
        
        return results
    
    async def generate_all(self) -> list:
        """Generate all topics"""
        print("="*80)
        print("🎬 CINEMA & MEDIA STUDIES - CHAT GENERATION (v2.8)")
        print("="*80)
        print(f"\nConfiguration:")
        print(f"  Model: openai/gpt-4o-mini")
        print(f"  Max Concurrent: {MAX_CONCURRENT}")
        print(f"  Batch Size: {BATCH_SIZE}")
        print(f"  Batch Delay: {BATCH_DELAY_MS}ms")
        print(f"  Total target: {sum(t['count'] for t in TOPICS.values())} examples")
        
        all_results = []
        
        for topic, config in TOPICS.items():
            results = await self.generate_topic(topic, config)
            all_results.extend(results)
        
        return all_results
    
    def save_results(self, results: list, output_path: str):
        """Save results to JSONL"""
        print(f"\n💾 Saving {len(results)} examples to: {output_path}")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
        
        print(f"✅ Saved successfully")
        print(f"\n📊 Final Statistics:")
        print(f"  Generated: {self.generated_count}")
        print(f"  Failed: {self.failed_count}")
        print(f"  Success rate: {(self.generated_count / (self.generated_count + self.failed_count) * 100):.1f}%")

async def main():
    generator = CinemaMediaChatGenerator()
    results = await generator.generate_all()
    generator.save_results(results, "../output/cinema_media_chat.jsonl")

if __name__ == "__main__":
    asyncio.run(main())
