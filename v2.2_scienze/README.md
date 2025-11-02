# v2.2 - Sciences Specialization

**Examples**: 10,000  
**Focus**: Biology, Chemistry, Physics, Mathematics  
**API**: Claude Haiku 4.5  
**Concurrency**: 30 parallel  
**Status**: ✅ Completed  

## Topics (4 Science Domains)

- **Biologia** (2,500 examples)
- **Chimica** (2,500 examples)
- **Fisica** (2,500 examples)
- **Matematica** (2,500 examples)

## Task Types

- Chat/RAG responses
- Quiz questions
- Citations with sources
- Cloze tests
- Reasoning questions
- Function calling

## Usage

```bash
cd scripts
python3 generator_chat.py
python3 generator_quiz.py
# ... other generators
```

## Configuration

- **Batch Size**: 100
- **Concurrent**: 30
- **Temperature**: 0.9
- **Max Tokens**: 6000
