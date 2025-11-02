"""
MEDICINA CHAT Generator - Conversazioni cliniche di ALTA QUALITÀ
Target: 12,000 esempi (24%)
"""
import json, time
from openrouter_client import OpenRouterClient
from load_secrets_books import prepare_for_generation
from tqdm import tqdm

class MedicinaChatGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, chunk: str, specialty: str) -> str:
        return f"""Sei un medico esperto e docente universitario. Genera 10 conversazioni ECCELLENTI di Q&A cliniche su {specialty.upper()}.

CONTENUTO CLINICO:
{chunk[:3000]}

OUTPUT (JSON):
[
  {{
    "question": "Domanda clinica complessa che uno studente di medicina farebbe (richiede ragionamento clinico, non semplice mnemonicità)",
    "answer": "Risposta clinica ECCELLENTE che:\n1. Spiega fisiopatologia e meccanismi\n2. Fornisce esempi di casi clinici reali\n3. Discute diagnosi differenziale\n4. Include 2-3 domande socratiche per stimolare ragionamento clinico\n5. Usa tono pedagogico, professionale, empatico\n6. Lunghezza: 200-300 parole\n7. Conclude con suggerimenti di approfondimento"
  }}
]

ESEMPI DI QUALITÀ:

DOMANDA MEDIOCRE: "Cos'è l'infarto miocardico?"
DOMANDA ECCELLENTE: "Come distinguere clinicamente un infarto STEMI da una sindrome coronarica acuta NSTEMI, e quali sono le implicazioni terapeutiche immediate?"

RISPOSTA MEDIOCRE: "L'infarto STEMI ha sopraslivellamento ST all'ECG, il NSTEMI no."
RISPOSTA ECCELLENTE: "La distinzione tra STEMI e NSTEMI è cruciale perché determina la strategia terapeutica immediata. Il STEMI (ST-Elevation MI) presenta dolore toracico tipico + sopraslivellamento ST ≥1mm in almeno 2 derivazioni contigue all'ECG. Questo indica occlusione coronarica completa → necessita riperfusione immediata (PCI primaria entro 90 min o fibrinolisi entro 30 min). Il NSTEMI invece mostra ECG con sottolivellamento ST o inversione T + troponina elevata, ma senza sopraslivellamento → occlusione parziale. Il timing della rivascolarizzazione dipende dal rischio (score GRACE): alto rischio → PCI entro 24h, rischio intermedio → 72h. [Caso pratico] Paziente 65 anni, dolore toracico da 2 ore, ECG con sopraslivellamento ST in V1-V4 → STEMI anteriore esteso → cateterismo immediato. Se stesso paziente con ECG normale ma troponina 50 ng/L (normale <14) → NSTEMI → stabilizzazione medica + strategia invasiva entro 24-72h. [Domande socratiche] Perché il STEMI richiede riperfusione IMMEDIATA mentre il NSTEMI può attendere? Come influisce la localizzazione (anteriore vs inferiore) sul rischio? [Approfondimento] Studiare le linee guida ESC 2023 sulle sindromi coronariche acute per algoritmi decisionali aggiornati."

REGOLE CRITICHE:
1. Questions: SEMPRE cliniche, mai teoriche pure
2. Answers: SEMPRE con ragionamento + esempi + DD
3. Tono: Clinico, pedagogico, socratico
4. Lunghezza: 200-300 parole per answer
5. NO risposte da manuale, SÌ risposte da clinico esperto

Genera 10 conversazioni cliniche ECCELLENTI."""
    
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
    
    def format_for_training(self, chat: dict, specialty: str) -> dict:
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "Sei ALL1E TUTOR MEDICINA, assistente clinico esperto e docente universitario."
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
    
    def generate_batch(self, chunk: str, specialty: str):
        prompt = self.create_prompt(chunk, specialty)
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.generate(messages, temperature=0.8, max_tokens=10000)
            chat_list = self.parse_response(response)
            return [self.format_for_training(c, specialty) for c in chat_list 
                    if 'question' in c and 'answer' in c and len(c['answer']) > 200]
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)
            return []
    
    def generate(self, target: int = 12000):
        print(f"\n{'='*80}")
        print(f"📝 MEDICINA CHAT GENERATOR - Target: {target:,} examples")
        print(f"{'='*80}\n")
        
        # Load books
        books = prepare_for_generation()
        output_path = "output/medicina_chat.jsonl"
        
        all_chats = []
        
        with open(output_path, 'a', encoding='utf-8') as f:
            for book in books:
                if len(all_chats) >= target:
                    break
                
                print(f"\n📚 Book: {book['title']}")
                
                for chunk in tqdm(book['chunks'], desc=f"Chat: {book['title'][:30]}"):
                    if len(all_chats) >= target:
                        break
                    
                    batch = self.generate_batch(chunk['text'], book['specialty'])
                    
                    for example in batch:
                        if len(all_chats) >= target:
                            break
                        f.write(json.dumps(example, ensure_ascii=False) + '\n')
                        f.flush()
                        all_chats.append(example)
                    
                    time.sleep(2)  # Rate limiting
                
                print(f"   ✅ Generated: {len(all_chats):,} / {target:,}")
        
        print(f"\n{'='*80}")
        print(f"✅ MEDICINA CHAT COMPLETE: {len(all_chats):,} examples")
        print(f"{'='*80}\n")
        
        return len(all_chats)

if __name__ == "__main__":
    generator = MedicinaChatGenerator()
    total = generator.generate(target=12000)
    print(f"\n🎉 Generated {total:,} medicina chat examples!")
