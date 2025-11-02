"""
CHAT/RAG Generator MEDICINA - Conversazioni cliniche di ALTA QUALITÀ
Target: 12,000 esempi da 26 libri Secrets/WAU
"""
import json, time
from openrouter_client import OpenRouterClient
from load_secrets_books import prepare_for_generation
from tqdm import tqdm

class ChatMedicinaGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, chunk: str, specialty: str) -> str:
        return f"""Sei un medico esperto e docente universitario. Genera 10 conversazioni CLINICHE ECCELLENTI in italiano su {specialty.upper()}.

CONTENUTO CLINICO:
{chunk[:3000]}

OUTPUT (JSON):
[
  {{
    "question": "Domanda clinica complessa che richiede ragionamento clinico (NO domande mnemoniche banali)",
    "answer": "Risposta clinica ECCELLENTE che:\\n1. Spiega fisiopatologia e meccanismi\\n2. Usa casi clinici reali ed esempi pratici\\n3. Include diagnosi differenziale\\n4. Integra 2-3 domande socratiche\\n5. Tono pedagogico ma clinico (200-300 parole)\\n6. Conclude con invito a approfondire"
  }}
]

ESEMPI DI QUALITÀ:

DOMANDA MEDIOCRE: "Cos'è l'infarto miocardico?"
DOMANDA ECCELLENTE: "Come distinguere clinicamente un infarto STEMI da una sindrome coronarica acuta NSTEMI, e quali sono le implicazioni terapeutiche immediate?"

RISPOSTA MEDIOCRE: "L'infarto STEMI ha sopraslivellamento ST all'ECG, il NSTEMI no."
RISPOSTA ECCELLENTE: "La distinzione tra STEMI e NSTEMI è cruciale perché determina la strategia terapeutica immediata. Il STEMI presenta dolore toracico tipico + sopraslivellamento ST ≥1mm in almeno 2 derivazioni contigue. Questo indica occlusione coronarica completa → necessita riperfusione immediata (PCI primaria entro 90 min o fibrinolisi entro 30 min). Il NSTEMI invece mostra ECG con sottolivellamento ST o inversione T + troponina elevata → occlusione parziale. [Caso pratico] Paziente 65 anni, dolore toracico da 2 ore, ECG con sopraslivellamento ST in V1-V4 → STEMI anteriore → cateterismo immediato. [Domande socratiche] Perché il STEMI richiede riperfusione IMMEDIATA mentre il NSTEMI può attendere? Come influisce la localizzazione sul rischio? [Invito] Esplorare i criteri GRACE e TIMI per stratificazione del rischio nelle SCA."

REGOLE CRITICHE:
1. Questions: SEMPRE cliniche, mai teoriche pure
2. Answers: SEMPRE con ragionamento + casi + DD
3. Tono: Clinico, pedagogico, socratico
4. Lunghezza: 200-300 parole per answer
5. NO risposte da manuale, SÌ risposte da clinico esperto

Genera 10 conversazioni cliniche ECCELLENTI."""
    
    def sanitize_json_text(self, text: str) -> str:
        """Remove control characters that break JSON parsing"""
        import re
        return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', ' ', text)
    
    def parse_response(self, response: str):
        import re
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
    
    def format_for_training(self, chat: dict, specialty: str) -> dict:
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "Sei ALL1E TUTOR MEDICINA, assistente clinico esperto e socratico."
                },
                {
                    "role": "user",
                    "content": chat['question']
                },
                {
                    "role": "assistant",
                    "content": chat['answer']
                }
            ],
            "metadata": {
                "type": "medicina_chat_clinical",
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
            response = self.client.generate(messages, temperature=0.8, max_tokens=10000)
            chat_list = self.parse_response(response)
            return [self.format_for_training(c, specialty) for c in chat_list if 'question' in c and 'answer' in c and len(c['answer']) > 200]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate_all(self, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} EXCELLENT medicina chat\n{'='*80}")
        
        data = prepare_for_generation()
        chunks = data['chunks']
        
        all_chats = []
        
        for chunk in tqdm(chunks, desc="  Medicina Chat"):
            if len(all_chats) >= target:
                break
            
            specialty = chunk.get('specialty', 'medicina')
            batch = self.generate_batch(chunk['text'], specialty)
            all_chats.extend(batch)
            
            if len(all_chats) % 100 == 0:
                with open(output_path, 'w', encoding='utf-8') as f:
                    for c in all_chats:
                        f.write(json.dumps(c, ensure_ascii=False) + '\n')
                print(f"   💾 Saved {len(all_chats)}")
            
            time.sleep(0.1)  # Optimized rate limiting
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for c in all_chats[:target]:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Generated {len(all_chats[:target])} excellent medicina chat")
        return all_chats[:target]

def main():
    print("="*80 + "\n🚀 MEDICINA CHAT GENERATOR - CONVERSAZIONI CLINICHE\n" + "="*80)
    generator = ChatMedicinaGenerator()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2.1_generation/output"
    
    target = 12000
    output = f"{output_dir}/chat_medicina.jsonl"
    generator.generate_all(target, output)
    
    print("\n✅ MEDICINA CHAT GENERATION COMPLETE")

if __name__ == "__main__":
    main()
