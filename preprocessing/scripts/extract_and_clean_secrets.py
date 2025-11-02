"""
Extract Secrets Medicina books from ALL1E database
Clean and prepare for HuggingFace dataset
"""

import json
import re
from typing import List, Dict
import os

# Get database URL from environment
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/all1e")

def extract_secrets_books() -> List[Dict]:
    """Extract all Secrets medicina books from database"""
    
    print("📚 Extracting Secrets/WAU medicina books from database...")
    
    # Use MCP postgres query instead
    # This will be called manually with proper query
    
    print("   Run this query to extract books:")
    print("""
    SELECT 
        id,
        title,
        filename,
        content,
        status,
        LENGTH(content) as content_length,
        created_at
    FROM knowledge_documents
    WHERE created_at > NOW() - INTERVAL '4 hours'
    AND status IN ('AWAITING_USER', 'COMPLETE')
    ORDER BY created_at DESC;
    """)
    
    return []

def clean_content(content: str) -> str:
    """Clean content: remove images, legends, quiz codes - keep ONLY text + formulas + tables"""
    
    # Remove image markers (all formats)
    # Format: ![Image: description]
    content = re.sub(r'!\[Image:.*?\]', '', content, flags=re.IGNORECASE)
    
    # Remove bbox annotations
    # Format: <!-- bbox: [x, y, w, h] -->
    content = re.sub(r'<!--\s*bbox:.*?-->', '', content)
    
    # Remove ALL "Figura X.Y" references (inline and standalone)
    # Examples: (Figura 1.1), Figura 1.1, (Fig. 1.1), Fig 1.1
    content = re.sub(r'\(?\s*Fig(?:ura)?\.?\s+\d+\.\d+\s*\)?', '', content, flags=re.IGNORECASE)
    
    # Remove quiz codes
    # Format: [SSM14183], [ABC123], etc.
    content = re.sub(r'\[([A-Z]{2,})\d+\]', '', content)
    
    # Remove "Tabella X.Y" captions (but keep the table content!)
    # Only remove the caption text, not the actual table
    content = re.sub(r'Tabella\s+\d+\.\d+\s*[^\n]*', '', content, flags=re.IGNORECASE)
    
    # Remove legend sections
    # Format: "Legenda:" followed by content until next section
    content = re.sub(r'^Legenda:.*?(?=\n\n|\n#|$)', '', content, flags=re.MULTILINE | re.DOTALL)
    
    # Remove image captions
    # Format: "Immagine 1:", "Foto:", "Illustrazione:"
    content = re.sub(r'(?:Immagine|Foto|Illustrazione)\s+\d+:.*?(?=\n\n|\n#|$)', '', content, flags=re.IGNORECASE)
    
    # Clean up extra punctuation left by removals
    content = re.sub(r'\s+([.,;:])', r'\1', content)  # Fix spacing before punctuation
    content = re.sub(r'([.,;:])\s*([.,;:])', r'\1', content)  # Remove duplicate punctuation
    
    # Remove multiple blank lines (keep max 1 blank line)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Remove lines with only whitespace
    content = re.sub(r'^\s*$\n', '', content, flags=re.MULTILINE)
    
    # Trim whitespace
    content = content.strip()
    
    return content

def extract_specialty(title: str) -> str:
    """Extract medical specialty from title"""
    
    # Map common patterns
    specialty_map = {
        "anestesia": "anestesia_rianimazione",
        "rianimazione": "anestesia_rianimazione",
        "farmacologia": "farmacologia",
        "chirurgia": "chirurgia_plastica",
        "cardiologia": "cardiologia",
        "psichiatria": "psichiatria",
        "ginecologia": "ginecologia_ostetricia",
        "ostetricia": "ginecologia_ostetricia",
        "urologia": "urologia",
        "oncologia": "oncologia_immunologia",
        "immunologia": "oncologia_immunologia",
        "genetica": "oncologia_immunologia",
        "ematologia": "ematologia",
        "igiene": "igiene_statistica",
        "statistica": "igiene_statistica",
        "epidemiologia": "igiene_statistica",
        "pneumologia": "pneumologia",
        "ortopedia": "ortopedia",
        "oftalmologia": "oftalmologia",
        "neurologia": "neurologia_neurochirurgia",
        "neurochirurgia": "neurologia_neurochirurgia",
        "nefrologia": "nefrologia",
        "dermatologia": "dermatologia",
        "endocrinologia": "endocrinologia",
        "otorinolaringoiatria": "otorinolaringoiatria",
        "pediatria": "pediatria",
        "gastroenterologia": "gastroenterologia",
        "infettive": "malattie_infettive",
        "chimica": "chimica",
        "biologia": "biologia"
    }
    
    title_lower = title.lower()
    
    for keyword, specialty in specialty_map.items():
        if keyword in title_lower:
            return specialty
    
    return "medicina_generale"

def prepare_for_huggingface(books: List[Dict]) -> List[Dict]:
    """Prepare books for HuggingFace dataset format"""
    
    print("\n🧹 Cleaning and formatting books...")
    
    dataset = []
    
    for book in books:
        # Clean content
        clean_text = clean_content(book['content'])
        
        # Extract specialty
        specialty = extract_specialty(book['title'])
        
        # Estimate tokens (rough: 1 token ~= 4 chars in Italian)
        token_count = len(clean_text) // 4
        
        # Format for HuggingFace
        entry = {
            "file_title": book['title'].replace('.pdf', '').replace('Copia_di_', ''),
            "text": clean_text,
            "token_count": token_count,
            "source": "secrets" if "secrets" in book['title'].lower() else "wau",
            "specialty": specialty,
            "original_filename": book['filename']
        }
        
        dataset.append(entry)
        
        print(f"   ✅ {entry['file_title']}")
        print(f"      Specialty: {specialty}")
        print(f"      Tokens: {token_count:,}")
        print(f"      Source: {entry['source']}")
    
    return dataset

def save_dataset(dataset: List[Dict], output_path: str):
    """Save dataset as JSON"""
    
    print(f"\n💾 Saving dataset to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved {len(dataset)} books")
    
    # Print summary
    total_tokens = sum(book['token_count'] for book in dataset)
    print(f"\n📊 Summary:")
    print(f"   Total books: {len(dataset)}")
    print(f"   Total tokens: {total_tokens:,}")
    print(f"   Avg tokens/book: {total_tokens // len(dataset):,}")
    
    # Group by specialty
    specialties = {}
    for book in dataset:
        spec = book['specialty']
        if spec not in specialties:
            specialties[spec] = 0
        specialties[spec] += 1
    
    print(f"\n📚 By specialty:")
    for spec, count in sorted(specialties.items()):
        print(f"   {spec}: {count} books")

if __name__ == "__main__":
    print("="*80)
    print("🔬 SECRETS/WAU MEDICINA DATASET PREPARATION")
    print("="*80)
    
    print("\n📋 Instructions:")
    print("1. Wait for ALL PDF to finish processing on ALL1E")
    print("2. Run database query to extract books")
    print("3. Pass extracted books to prepare_for_huggingface()")
    print("4. Save dataset with save_dataset()")
    print("5. Upload to HuggingFace")
    
    print("\n⏸️  Waiting for your manual extraction...")
    print("   (Run query shown above and pass results to this script)")
