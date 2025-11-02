"""
Extract Cinema & Media Studies documents from ALL1E database
Clean and prepare for v2.8 dataset generation
"""

import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from preprocessing.scripts.extract_and_clean_secrets import clean_content

def extract_cinema_media_docs():
    """
    Extract cinema/media documents from database
    
    Documents to extract (7 total):
    1. Storia del cinema (Thompson & Bordwell) - 2.5 MB
    2. Cinema italiano 1905-2023 (Brunetta) - 1.5 MB
    3. Manuale del film (Rondolino) - 975 KB
    4. Metafora e vita quotidiana (Lakoff & Johnson) - 565 KB
    5. Il cinema italiano (Costa) - 290 KB
    6. Teorie comunicazioni di massa - 146 KB
    7. Sociologia Comunicazione digitale - 84 KB
    """
    
    print("="*80)
    print("🎬 CINEMA & MEDIA STUDIES DATASET EXTRACTION (v2.8)")
    print("="*80)
    
    # Document IDs from database query
    document_ids = [
        "doc_1762123957821_rqww8",  # Storia del cinema
        "doc_1762119148808_muvi2",  # Cinema italiano
        "doc_1762119151704_prza4",  # Manuale del film
        "doc_1762123956099_vid2s",  # Metafora e vita quotidiana
        "doc_1762119150619_0jb6d",  # Il cinema italiano
        "doc_1762124627119_olgwm",  # Teorie comunicazioni
        "doc_1762119152832_zyp1d"   # Sociologia Comunicazione
    ]
    
    print(f"\n📚 Documents to extract: {len(document_ids)}")
    print("\n⚠️  MANUAL STEP REQUIRED:")
    print("   Run this PostgreSQL query to extract documents:")
    print()
    print("   SELECT id, title, filename, content")
    print("   FROM knowledge_documents")
    print("   WHERE id IN (")
    for i, doc_id in enumerate(document_ids):
        comma = "," if i < len(document_ids) - 1 else ""
        print(f"       '{doc_id}'{comma}")
    print("   );")
    print()
    print("   Then pass results to process_documents() function")
    print()
    
    return document_ids

def process_documents(raw_documents: list) -> list:
    """
    Process raw documents: clean and format
    
    Args:
        raw_documents: List of dicts with keys: id, title, filename, content
        
    Returns:
        List of cleaned documents ready for generation
    """
    
    print("\n🧹 Processing and cleaning documents...")
    
    cleaned_docs = []
    
    for doc in raw_documents:
        print(f"\n   📄 {doc['title']}")
        
        # Clean content
        clean_text = clean_content(doc['content'])
        
        # Determine category
        title_lower = doc['title'].lower()
        if any(word in title_lower for word in ['cinema', 'film', 'movie', 'regia']):
            category = 'cinema'
        elif any(word in title_lower for word in ['sociologia', 'comunicazione', 'media', 'massa']):
            category = 'sociologia_comunicazione'
        elif any(word in title_lower for word in ['metafora', 'linguistica', 'lakoff']):
            category = 'linguistica_cognitiva'
        else:
            category = 'cultura_generale'
        
        # Split into chunks (2000 chars per chunk)
        chunk_size = 2000
        chunks = []
        for i in range(0, len(clean_text), chunk_size):
            chunk_text = clean_text[i:i+chunk_size]
            if len(chunk_text.strip()) > 100:  # Skip very short chunks
                chunks.append({
                    "chunk_index": len(chunks),
                    "text": chunk_text,
                    "document_id": doc['id'],
                    "document_title": doc['title'].replace('.pdf', '').replace('Copia_di_', '')
                })
        
        cleaned_doc = {
            "id": doc['id'],
            "title": doc['title'].replace('.pdf', '').replace('Copia_di_', ''),
            "filename": doc['filename'],
            "category": category,
            "clean_text": clean_text,
            "original_length": len(doc['content']),
            "clean_length": len(clean_text),
            "chunk_count": len(chunks),
            "chunks": chunks
        }
        
        cleaned_docs.append(cleaned_doc)
        
        print(f"      Category: {category}")
        print(f"      Original: {cleaned_doc['original_length']:,} chars")
        print(f"      Cleaned: {cleaned_doc['clean_length']:,} chars")
        print(f"      Chunks: {cleaned_doc['chunk_count']}")
        print(f"      Reduction: {((1 - cleaned_doc['clean_length']/cleaned_doc['original_length']) * 100):.1f}%")
    
    return cleaned_docs

def save_dataset(cleaned_docs: list, output_path: str):
    """Save cleaned documents as JSON"""
    
    print(f"\n💾 Saving dataset to: {output_path}")
    
    dataset = {
        "version": "v2.8_cinema_media",
        "extraction_date": datetime.utcnow().isoformat(),
        "total_documents": len(cleaned_docs),
        "total_chunks": sum(doc['chunk_count'] for doc in cleaned_docs),
        "categories": {
            "cinema": sum(1 for doc in cleaned_docs if doc['category'] == 'cinema'),
            "sociologia_comunicazione": sum(1 for doc in cleaned_docs if doc['category'] == 'sociologia_comunicazione'),
            "linguistica_cognitiva": sum(1 for doc in cleaned_docs if doc['category'] == 'linguistica_cognitiva')
        },
        "documents": cleaned_docs
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved {dataset['total_documents']} documents")
    print(f"✅ Total chunks: {dataset['total_chunks']:,}")
    
    print(f"\n📊 Summary by category:")
    for cat, count in dataset['categories'].items():
        print(f"   {cat}: {count} documents")
    
    return dataset

if __name__ == "__main__":
    print("\n📋 Step 1: Extract document IDs")
    document_ids = extract_cinema_media_docs()
    
    print("\n📋 Step 2: Manual extraction required")
    print("   Copy the SQL query above and run it in PostgreSQL")
    print("   Then call: process_documents(raw_documents)")
    print()
    print("📋 Step 3: After processing, save with:")
    print("   save_dataset(cleaned_docs, 'output/cinema_media_dataset.json')")
