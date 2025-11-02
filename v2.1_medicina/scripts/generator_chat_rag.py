"""
CHAT/RAG Generator - Conversazioni educative di ALTA QUALITÀ
Modalità più usata! Deve essere ECCELLENTE
"""
import json, time
from openrouter_client import OpenRouterClient
from load_simone_books import load_simone_textbooks, chunk_text
from tqdm import tqdm

class ChatRAGGenerator:
    def __init__(self):
        self.client = OpenRouterClient()
    
    def create_prompt(self, chunk: str, subject: str) -> str:
        return f"""Sei un esperto educativo. Genera 10 conversazioni ECCELLENTI di Q&A su {subject.upper()}.

CONTENUTO EDUCATIVO:
{chunk[:3000]}

OUTPUT (JSON):
[
  {{
    "question": "Domanda complessa e realistica che uno studente farebbe (richiede comprensione profonda, non semplice definizione)",
    "answer": "Risposta educativa ECCELLENTE che:\n1. Spiega il concetto con chiarezza e profondità\n2. Usa esempi pratici e applicazioni reali\n3. Fa collegamenti inter-disciplinari\n4. Include 2-3 domande socratiche per stimolare riflessione\n5. Usa tono pedagogico, incoraggiante, empatico\n6. Lunghezza: 200-300 parole\n7. Conclude con invito a esplorare ulteriormente"
  }}
]

ESEMPI DI QUALITÀ:

DOMANDA MEDIOCRE: "Cos'è il diritto tributario?"
DOMANDA ECCELLENTE: "Come il sistema tributario italiano bilancia l'esigenza di equità fiscale con la necessità di incentivare la crescita economica?"

RISPOSTA MEDIOCRE: "Il diritto tributario regola le tasse. Include imposte dirette e indirette."
RISPOSTA ECCELLENTE: "Il sistema tributario italiano affronta una sfida complessa: da un lato deve garantire equità fiscale (chi più ha, più contribuisce), dall'altro deve incentivare investimenti e crescita. Questo bilanciamento si realizza attraverso diversi meccanismi. Le imposte progressive (come IRPEF) assicurano che il carico fiscale sia proporzionato al reddito, mentre detrazioni e deduzioni mirate (es: ricerca e sviluppo, investimenti green) stimolano comportamenti economicamente virtuosi. È come un sistema di equilibri: troppa tassazione scoraggia l'iniziativa, troppo poca compromette i servizi pubblici. Pensiamo alle startup innovative: godono di agevolazioni fiscali nei primi anni per compensare i rischi elevati. Questo crea un circolo virtuoso: più innovazione → più occupazione → più base imponibile futura. [Domande socratiche] Come pensi che la globalizzazione influenzi questo equilibrio? Quali altri Paesi hanno trovato soluzioni innovative? [Invito] Esplorare casi concreti di paesi scandinavi o asiatici può offrire spunti interessanti su modelli alternativi."

REGOLE CRITICHE:
1. Questions: SEMPRE complesse, mai banali
2. Answers: SEMPRE pedagogiche con esempi pratici
3. Tono: Socratico, incoraggiante, professionale
4. Lunghezza: 200-300 parole per answer
5. NO risposte enciclopediche, SÌ risposte educative

Genera 10 conversazioni ECCELLENTI."""
    
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
    
    def format_for_training(self, chat: dict, subject: str) -> dict:
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "Sei ALL1E TUTOR, assistente educativo esperto e socratico."
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
                "type": "chat_rag_standard",
                "subject": subject,
                "source": "simone_textbooks",
                "quality": "excellent"
            }
        }
    
    def generate_batch(self, chunk: str, subject: str):
        prompt = self.create_prompt(chunk, subject)
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.generate(messages, temperature=0.8, max_tokens=10000)
            chat_list = self.parse_response(response)
            return [self.format_for_training(c, subject) for c in chat_list if 'question' in c and 'answer' in c and len(c['answer']) > 200]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def generate_for_subject(self, books, subject: str, target: int, output_path: str):
        print(f"\n{'='*80}\n📝 Generating {target} EXCELLENT chat/rag for: {subject.upper()}\n{'='*80}")
        all_chats = []
        
        for book in books:
            print(f"\n📚 Book: {book['file_title']}")
            chunks = chunk_text(book['text'], 3000)
            needed = (target - len(all_chats)) // 10 + 1
            
            for chunk in tqdm(chunks[:needed], desc="  Generating"):
                if len(all_chats) >= target:
                    break
                batch = self.generate_batch(chunk, subject)
                all_chats.extend(batch)
                if len(all_chats) % 100 == 0:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for c in all_chats:
                            f.write(json.dumps(c, ensure_ascii=False) + '\n')
                    print(f"   💾 Saved {len(all_chats)}")
                time.sleep(0.1)  # Optimized
            
            if len(all_chats) >= target:
                break
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for c in all_chats[:target]:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Generated {len(all_chats[:target])} excellent chat/rag")
        return all_chats[:target]

def main():
    print("="*80 + "\n🚀 CHAT/RAG GENERATOR - CONVERSAZIONI ECCELLENTI\n" + "="*80)
    generator = ChatRAGGenerator()
    categories = load_simone_textbooks()
    output_dir = "/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2_dataset_generation/output"
    
    # Genera per TUTTE le materie
    targets = {
        "diritto": 10000,
        "economia": 5000, 
        "cultura_generale": 3000,
        "scienze": 2000
    }
    
    for subject, count in targets.items():
        if categories.get(subject):
            output = f"{output_dir}/chat_rag_{subject}.jsonl"
            generator.generate_for_subject(categories[subject], subject, count, output)
    
    print("\n✅ CHAT/RAG GENERATION COMPLETE")

if __name__ == "__main__":
    main()
