"""
Extract chunks with formulas (LaTeX $...$) from Pinecone
For chemistry, physics, and mathematics formulas training
"""

import json
import os
from pinecone import Pinecone

def extract_formula_chunks():
    """Extract chunks containing LaTeX formulas from Pinecone"""
    
    # Initialize Pinecone
    api_key = os.environ.get('PINECONE_API_KEY', 'pcsk_2BCsQJ_4AXZnSZ26JXfk2Qij43yNFkW4FoPyVWE5GBc9FoSADwCHxQyNkCsLnQRs8GaE3b')
    pc = Pinecone(api_key=api_key)
    
    index = pc.Index('all1e-docling')
    
    print("🔬 Extracting chunks with formulas from Pinecone...")
    print("   Index: all1e-docling")
    print("")
    
    # Query all namespaces (admin has most scientific content)
    namespaces = ['admin']
    
    all_formula_chunks = []
    
    for namespace in namespaces:
        print(f"📚 Scanning namespace: {namespace}")
        
        # We'll query in batches using dummy vectors
        # Since we can't filter by text content directly, we query broadly
        # and filter in Python
        
        try:
            # Query with dummy vector (zeros) to get random samples
            results = index.query(
                vector=[0.0] * 768,  # Embedding dimension
                top_k=10000,  # Get many results
                namespace=namespace,
                include_metadata=True
            )
            
            print(f"   Retrieved {len(results['matches'])} chunks")
            
            # Filter chunks with $ (LaTeX formulas)
            for match in results['matches']:
                metadata = match.get('metadata', {})
                text = metadata.get('text', '')
                
                # Check if contains LaTeX formulas
                if '$' in text and '\\' in text:  # LaTeX syntax
                    # Categorize formula type
                    formula_type = 'unknown'
                    text_lower = text.lower()
                    
                    # Chemistry keywords
                    if any(kw in text_lower for kw in ['carboidrat', 'legame', 'molecola', 'atomo', 'idrogeno', 'ossigeno', 'carbonio', 'reazione', 'ph', 'ione']):
                        formula_type = 'chemistry'
                    # Physics keywords
                    elif any(kw in text_lower for kw in ['forza', 'energia', 'velocità', 'accelerazione', 'massa', 'legge', 'newton', 'termodinamica', 'meccanica', 'onda']):
                        formula_type = 'physics'
                    # Math keywords
                    elif any(kw in text_lower for kw in ['integrale', 'derivata', 'equazione', 'funzione', 'limite', 'somma', 'prodotto', 'serie', 'matrice']):
                        formula_type = 'mathematics'
                    # Default to chemistry if has chemical symbols
                    elif any(sym in text for sym in ['\\mathrm{C}', '\\mathrm{H}', '\\mathrm{O}', '\\mathrm{N}', '\\alpha', '\\beta']):
                        formula_type = 'chemistry'
                    else:
                        # Generic scientific
                        formula_type = 'general'
                    
                    chunk_data = {
                        'chunk_id': match['id'],
                        'text': text,
                        'formula_type': formula_type,
                        'document_id': metadata.get('document_id'),
                        'chunk_index': metadata.get('chunk_index'),
                        'topic_name': metadata.get('topic_name'),
                        'headers': metadata.get('headers', [])
                    }
                    
                    all_formula_chunks.append(chunk_data)
        
        except Exception as e:
            print(f"   ⚠️ Error querying {namespace}: {e}")
    
    print(f"\n✅ Extracted {len(all_formula_chunks)} chunks with formulas")
    
    # Count by type
    by_type = {}
    for chunk in all_formula_chunks:
        ftype = chunk['formula_type']
        by_type[ftype] = by_type.get(ftype, 0) + 1
    
    print("\n📊 Distribution:")
    for ftype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        print(f"   {ftype}: {count}")
    
    # Save to file
    output_path = 'formula_chunks.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_formula_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved to: {output_path}")
    print(f"   Total chunks: {len(all_formula_chunks)}")
    
    return all_formula_chunks

if __name__ == "__main__":
    extract_formula_chunks()
