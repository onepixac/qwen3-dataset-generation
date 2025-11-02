# Preprocessing Tools

> Scripts for extracting and cleaning PDF chunks from ALL1E database before dataset generation

## 📊 Overview

When admins upload PDF documents to ALL1E, these tools extract the processed chunks and clean them for fine-tuning dataset generation.

**Purpose**:
- Extract document chunks from PostgreSQL database
- Clean content (remove images, legends, quiz codes)
- Preserve educational content (text, formulas, tables)
- Format for dataset generation

---

## 🛠️ Available Scripts

### 1. extract_and_clean_secrets.py

**Purpose**: Extract and clean Secrets/WAU medicina books

**Features**:
- ✅ Removes image markers: `![Image: description]`
- ✅ Removes bbox annotations: `<!-- bbox: [x, y, w, h] -->`
- ✅ Removes figure references: `(Figura 1.1)`, `Fig. 1.1`
- ✅ Removes quiz codes: `[SSM14183]`, `[ABC123]`
- ✅ Removes table captions (keeps table content)
- ✅ Removes legend sections
- ✅ Cleans punctuation and spacing
- ✅ Extracts medical specialty from title
- ✅ Formats for HuggingFace dataset

**Usage**:
```python
from extract_and_clean_secrets import clean_content, prepare_for_huggingface

# Clean raw content
clean_text = clean_content(raw_content)

# Prepare for dataset
books = [{"title": "...", "content": "...", "filename": "..."}]
dataset = prepare_for_huggingface(books)
```

**Output Format**:
```json
{
  "file_title": "Secrets Cardiologia",
  "text": "Cleaned text content...",
  "token_count": 125000,
  "source": "secrets",
  "specialty": "cardiologia",
  "original_filename": "secrets_cardiologia.pdf"
}
```

---

### 2. extract_formula_chunks.py

**Purpose**: Extract mathematical formula chunks from documents

**Features**:
- Extract LaTeX formulas from Markdown
- Identify formula context (before/after text)
- Clean and normalize LaTeX syntax
- Group related formulas

**Usage**:
```python
from extract_formula_chunks import extract_formulas

chunks = extract_formulas(document_content)
# Returns list of formula chunks with context
```

---

### 3. extract_books_final.py

**Purpose**: Extract engineering books from database

**Features**:
- Query PostgreSQL for recent uploads
- Filter by document status (COMPLETE)
- Extract metadata (title, filename, content)
- Batch processing for multiple books

**Usage**:
```bash
python3 extract_books_final.py
```

---

## 🗄️ Database Query

**PostgreSQL query to extract uploaded documents**:

```sql
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
```

**Environment**:
```bash
DATABASE_URL="postgresql://user:pass@host:5432/all1e"
```

---

## 🧹 Cleaning Patterns

### Removed Content

| Pattern | Example | Regex |
|---------|---------|-------|
| Images | `![Image: anatomia]` | `!\[Image:.*?\]` |
| Bbox | `<!-- bbox: [1,2,3,4] -->` | `<!--\s*bbox:.*?-->` |
| Figures | `(Figura 1.1)` | `\(?\s*Fig(?:ura)?\.?\s+\d+\.\d+\s*\)?` |
| Quiz codes | `[SSM14183]` | `\[([A-Z]{2,})\d+\]` |
| Table captions | `Tabella 1.1 - Descrizione` | `Tabella\s+\d+\.\d+\s*[^\n]*` |
| Legends | `Legenda: ...` | `^Legenda:.*?(?=\n\n\|\n#\|$)` |

### Preserved Content

✅ **Keep**:
- All text content
- LaTeX formulas (`$...$`, `$$...$$`)
- Markdown tables
- Headers and structure
- Educational explanations

---

## 🔄 Workflow

```
1. Admin uploads PDF to ALL1E
   ↓
2. Mistral OCR processes PDF
   ↓
3. Docling chunks content
   ↓
4. Content stored in PostgreSQL
   ↓
5. Run extraction script (this tool)
   ↓
6. Clean and format content
   ↓
7. Use with generator scripts (v2.x)
   ↓
8. Generate fine-tuning examples
```

---

## 📝 Example Output

### Before Cleaning

```markdown
# Capitolo 1 - Cardiologia

![Image: anatomia cuore]<!-- bbox: [100, 200, 300, 400] -->

Il cuore è un organo muscolare (Figura 1.1) che pompa sangue.

Tabella 1.1 - Valvole cardiache
| Valvola | Posizione |
|---------|-----------|
| Mitrale | Sinistra  |

[SSM14183] Quale valvola si trova tra atrio e ventricolo sinistro?

Legenda: Le frecce indicano il flusso sanguigno
```

### After Cleaning

```markdown
# Capitolo 1 - Cardiologia

Il cuore è un organo muscolare che pompa sangue.

| Valvola | Posizione |
|---------|-----------|
| Mitrale | Sinistra  |
```

---

## 🚀 Integration with Generators

**Workflow with v2.x generators**:

```bash
# 1. Extract and clean chunks
cd preprocessing/scripts
python3 extract_and_clean_secrets.py

# Output: secrets_medicina_books.json

# 2. Use with generator
cd ../../v2.1_medicina/scripts
python3 generator_chat_medicina.py --input ../../preprocessing/secrets_medicina_books.json

# Generates: medicina_chat.jsonl
```

---

## 📊 Statistics

**Cleaning Impact** (typical Secrets medicina book):

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Content length | 250,000 chars | 180,000 chars | -28% |
| Images | 150 | 0 | -100% |
| Quiz codes | 200 | 0 | -100% |
| Figures refs | 150 | 0 | -100% |
| Table captions | 30 | 0 | -100% |
| Legends | 20 | 0 | -100% |
| **Educational text** | **✅ Preserved** | **✅ Preserved** | **0%** |

---

## 🔧 Customization

### Add New Cleaning Pattern

Edit `extract_and_clean_secrets.py`:

```python
def clean_content(content: str) -> str:
    # ... existing patterns ...
    
    # Add your pattern
    content = re.sub(r'YOUR_REGEX_PATTERN', '', content)
    
    return content
```

### Add New Specialty

Edit specialty mapping:

```python
specialty_map = {
    "your_keyword": "your_specialty",
    # ... existing mappings ...
}
```

---

## 📞 Support

For issues with preprocessing:
- Check database connection (DATABASE_URL)
- Verify document status in PostgreSQL
- Review cleaning patterns in scripts
- Contact: support@all1e.com

---

**Last Updated**: 2025-11-02 | **Status**: Production | **Version**: 1.0.0
