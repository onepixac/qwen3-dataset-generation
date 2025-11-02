"""
Extract Engineering Books from PostgreSQL - FINAL VERSION
Uses connection string from ecosystem.config.js
"""
import json
import psycopg2
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Database connection string (from ecosystem.config.js)
DATABASE_URL = "postgresql://all1eadmin:All1eDB2025@all1e-staging-db.cbi2uooo2xn1.eu-central-1.rds.amazonaws.com:5432/all1e_database?sslmode=require"

# Engineering books mapping
ENGINEERING_BOOKS = [
    ("doc_1762097176019_eoomm", "Meccanica razionale per l'ingegneria", "meccanica"),
    ("doc_1762097172689_x06pr", "Meccanica delle Strutture Volume 1", "meccanica"),
    ("doc_1762097171530_j4cgz", "Fondamenti di elettrotecnica", "elettrotecnica"),
    ("doc_1762097170532_kyocy", "Matematica Numerica 4th", "matematica_applicata"),
    ("doc_1762097166764_u04m7", "Fondamenti di Meccanica Teorica 3rd", "meccanica"),
    ("doc_1762097166631_6py77", "Fondamenti di Meccanica Teorica", "meccanica"),
    ("doc_1762097164163_zsa8m", "Elementi di fisica tecnica", "fisica_tecnica"),
    ("doc_1762097164076_q0ovj", "Esercitazioni di Analisi Matematica 2", "matematica_applicata"),
    ("doc_1762097161684_yodsw", "Esercizi di algebra lineare e geometria", "matematica_applicata"),
    ("doc_1762097160385_cdjah", "Disegno tecnico industriale 2", "disegno_tecnico"),
    ("doc_1762097159105_a9v3l", "Elementi di Fisica Meccanica e Termodinamica", "fisica_tecnica"),
    ("doc_1762097157002_lkxul", "Disegno tecnico industriale 1", "disegno_tecnico"),
    ("doc_1762097155212_hjqos", "Circuiti elettrici Alexander", "elettrotecnica"),
    ("doc_1762097152534_djdpq", "Circuiti elettrici Perfetti", "elettrotecnica"),
    ("doc_1762097151750_2igun", "Calcolo Differenziale 2 Adams", "matematica_applicata"),
    ("doc_1762097147198_t01o2", "Analisi Matematica 2 Giusti", "matematica_applicata"),
    ("doc_1762097146335_ywu1h", "Calcolo Scientifico MATLAB Octave", "calcolo_scientifico"),
    ("doc_1762097144313_g73i1", "Automatica Raccolta esercizi", "automatica"),
    ("doc_1762097143161_ljqjv", "Analisi Matematica Volume 2", "matematica_applicata"),
    ("doc_1762097141091_wilpf", "Algebra lineare Schlesinger", "matematica_applicata"),
    ("doc_1762097140242_dfhvq", "Analisi Matematica 2 Esercizi Boella", "matematica_applicata")
]

def chunk_text(text: str, chunk_size: int = 2500, overlap: int = 250) -> List[str]:
    """Split text into overlapping chunks"""
    if not text or len(text) < 200:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at boundary
        if end < len(text):
            paragraph_end = text.rfind("\n\n", start, end)
            if paragraph_end != -1 and paragraph_end > start + chunk_size // 2:
                end = paragraph_end
            else:
                line_end = text.rfind("\n", start, end)
                if line_end != -1 and line_end > start + chunk_size // 2:
                    end = line_end
                else:
                    sentence_end = text.rfind(". ", start, end)
                    if sentence_end != -1 and sentence_end > start + chunk_size // 2:
                        end = sentence_end + 1
        
        chunk = text[start:end].strip()
        
        if chunk and len(chunk) >= 200:
            # Clean up
            chunk = re.sub(r'\n{3,}', '\n\n', chunk)
            chunk = re.sub(r' {2,}', ' ', chunk)
            chunks.append(chunk)
        
        if end >= len(text):
            break
        start = end - overlap
    
    return chunks

def extract_books() -> List[Dict]:
    """Extract all engineering books from database"""
    print("\n" + "=" * 80)
    print("📚 ENGINEERING BOOKS EXTRACTION")
    print("=" * 80)
    print(f"   Total books: {len(ENGINEERING_BOOKS)}")
    print(f"   Chunk size: 2,500 chars | Overlap: 250 chars\n")
    
    all_chunks = []
    total_chars = 0
    books_processed = 0
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Extract document IDs
        doc_ids = [book[0] for book in ENGINEERING_BOOKS]
        book_map = {book[0]: (book[1], book[2]) for book in ENGINEERING_BOOKS}
        
        # Query all books
        query = """
        SELECT id, title, content
        FROM knowledge_documents
        WHERE id = ANY(%s)
        ORDER BY created_at DESC;
        """
        
        cursor.execute(query, (doc_ids,))
        results = cursor.fetchall()
        
        print(f"✅ Found {len(results)} books in database\n")
        
        # Process each book
        for doc_id, db_title, content in results:
            if doc_id not in book_map:
                continue
            
            title, domain = book_map[doc_id]
            
            print(f"📖 {title[:60]}")
            print(f"   ID: {doc_id}")
            print(f"   Domain: {domain}")
            
            if not content or len(content) < 1000:
                print(f"   ⚠️  Content too short ({len(content) if content else 0} chars), skipping\n")
                continue
            
            print(f"   Content: {len(content):,} chars")
            
            # Create chunks
            text_chunks = chunk_text(content, chunk_size=2500, overlap=250)
            print(f"   Chunks: {len(text_chunks)}")
            
            # Add chunks with metadata
            for i, chunk_content in enumerate(text_chunks):
                all_chunks.append({
                    "text": chunk_content,
                    "chunk_index": i,
                    "document_id": doc_id,
                    "document_title": title,
                    "domain": domain,
                    "source": "engineering_textbook",
                    "generation": "v2.4_ingegneria"
                })
            
            total_chars += len(content)
            books_processed += 1
            print(f"   ✅ Done\n")
        
        cursor.close()
        conn.close()
        
        print("=" * 80)
        print(f"✅ EXTRACTION COMPLETE")
        print(f"   Books processed: {books_processed}/{len(ENGINEERING_BOOKS)}")
        print(f"   Total chunks: {len(all_chunks):,}")
        print(f"   Total content: {total_chars / 1_000_000:.2f} MB")
        print(f"   Avg chunks/book: {len(all_chunks) // max(books_processed, 1)}")
        print("=" * 80 + "\n")
        
        return all_chunks
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise

def save_chunks(chunks: List[Dict], output_file: Path):
    """Save chunks to JSON file"""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    file_size = output_file.stat().st_size
    print(f"💾 CHUNKS SAVED")
    print(f"   File: {output_file}")
    print(f"   Size: {file_size / 1_000_000:.2f} MB")
    print(f"   Chunks: {len(chunks):,}\n")

def print_statistics(chunks: List[Dict]):
    """Print statistics"""
    # Domain distribution
    domains = {}
    for chunk in chunks:
        domain = chunk["domain"]
        domains[domain] = domains.get(domain, 0) + 1
    
    print(f"📊 DOMAIN DISTRIBUTION:")
    for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(chunks) * 100
        print(f"   {domain:25} {count:>6,} chunks ({percentage:>5.1f}%)")
    
    # Generation targets
    total = len(chunks)
    print(f"\n🎯 EXPECTED GENERATION TARGETS:")
    print(f"   Chat RAG:           {total * 10:>8,} examples (10 per chunk)")
    print(f"   Quiz:               {total:>8,} examples (1 per chunk)")
    print(f"   Reasoning:          {total:>8,} examples (1 per chunk)")
    print(f"   Function Calling:   {total // 5:>8,} examples (1 per 5 chunks)")
    print(f"   Cloze Tests:        {total:>8,} examples (1 per chunk)")
    print(f"   Formulas (GPT-4o):  {2_100:>8,} examples (separate)")
    print(f"   " + "-" * 50)
    print(f"   TOTAL:              {total * 13 + 2100:>8,} examples")
    
    print("\n✅ READY FOR DATASET GENERATION")
    print("   Next: ./start_generation.sh\n")

if __name__ == "__main__":
    try:
        # Extract books
        chunks = extract_books()
        
        if not chunks:
            print("❌ No chunks extracted!")
            exit(1)
        
        # Save chunks
        output_file = Path(__file__).parent / "checkpoints" / "ingegneria_chunks.json"
        save_chunks(chunks, output_file)
        
        # Print statistics
        print_statistics(chunks)
        
        print("✅ EXTRACTION SUCCESSFUL\n")
        
    except Exception as e:
        print(f"\n❌ EXTRACTION FAILED: {e}\n")
        exit(1)
