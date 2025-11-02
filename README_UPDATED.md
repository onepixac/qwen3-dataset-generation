# Qwen3 Fine-tuning Dataset Generation

> Complete toolkit for generating 220K+ high-quality Italian educational datasets using Claude Haiku 4.5

## 📊 Overview

This repository contains **all production scripts** used to generate **223,261 training examples** across 40+ distinct datasets for fine-tuning Qwen3-4B models for the ALL1E educational platform.

**Total Dataset**: **223,261 examples** across 40+ distinct datasets (8 major versions)

**Major Versions**:
- **v2.0**: Base + function calling + conversations (~80K examples)
- **v2.1**: Medical specialization (~38K examples)
- **v2.2**: Sciences (biology, chemistry, physics, math) (~35K examples)
- **v2.3**: Logic & critical thinking (~20K examples)
- **v2.4**: Engineering disciplines (~10K examples)
- **v2.5**: Emotional support (6,836 examples) ✅
- **v2.6**: Tone flexibility (~16K examples) 🔄
- **v2.7**: Humanities & soft skills (~8K examples) 🔄
- **Multidisciplinary**: Cross-domain datasets (~59K examples)

**Performance**:
- Generation cost: **~$600 USD** (Claude Haiku 4.5 API)
- Time: **~120 hours** (distributed parallel processing)
- Success rate: **99.2%** (valid JSON responses)
- Quality: **Production-ready** (validated with 88.11% token accuracy)

---
