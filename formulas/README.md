# Formulas - LaTeX Mathematical Notation

**Examples**: 207  
**Focus**: LaTeX formula rendering, mathematical notation  
**API**: GPT-4o (OpenAI) + Qwen2.5-Math-7B (HuggingFace)  
**Concurrency**: 5 parallel  
**Status**: ✅ Completed  

## Overview

High-quality LaTeX formula examples for training mathematical notation understanding.

**Two-phase generation**:
1. **GPT-4o**: Generate LaTeX formulas with educational context
2. **Qwen2.5-Math-7B**: Validate formula correctness

## Formula Categories

- Algebra (50)
- Calculus (50)
- Trigonometry (30)
- Linear Algebra (25)
- Statistics (20)
- Physics Equations (20)
- Chemistry Formulas (12)

## Scripts

- `generator_formulas_gpt4o.py` - Primary generator (GPT-4o)
- `generator_formulas_hf.py` - HuggingFace validation
- `generator_formulas_optimized.py` - Production version

## Usage

```bash
cd scripts
python3 generator_formulas_gpt4o.py
```

## Configuration

- **Batch Size**: 10
- **Concurrent**: 5
- **Temperature**: 0.7 (lower for precision)
- **Max Tokens**: 4000

## Cost

- **GPT-4o**: ~$5 USD for 207 examples
- **HuggingFace**: Free (Inference API)
