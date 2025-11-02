#!/bin/bash

# v2.8 Cinema & Media Studies - Run All Generators
# Using GPT-4o-mini via OpenRouter

echo "========================================================================"
echo "🎬 CINEMA & MEDIA STUDIES DATASET GENERATION (v2.8)"
echo "========================================================================"
echo ""
echo "Model: GPT-4o-mini (OpenRouter)"
echo "Target: 6,800 examples (COMPLETE dataset)"
echo "Estimated time: 10-14 hours"
echo "Estimated cost: ~$15 USD"
echo ""
echo "Starting generators in parallel..."
echo ""

# Create output directory
mkdir -p ../output
mkdir -p ../logs

# Start generators in background
echo "🎬 Starting Chat/RAG generator..."
python3 generator_chat.py > ../logs/chat.log 2>&1 &
CHAT_PID=$!

echo "📝 Starting Quiz generator..."
python3 generator_quiz.py > ../logs/quiz.log 2>&1 &
QUIZ_PID=$!

echo "📋 Starting Cloze generator..."
python3 generator_cloze.py > ../logs/cloze.log 2>&1 &
CLOZE_PID=$!

echo "🧠 Starting Reasoning generator..."
python3 generator_reasoning.py > ../logs/reasoning.log 2>&1 &
REASONING_PID=$!

echo "📚 Starting Citations generator..."
python3 generator_citations.py > ../logs/citations.log 2>&1 &
CITATIONS_PID=$!

echo "📖 Starting Sources generator..."
python3 generator_sources.py > ../logs/sources.log 2>&1 &
SOURCES_PID=$!

echo ""
echo "✅ All generators started!"
echo ""
echo "Process IDs:"
echo "  Chat: $CHAT_PID"
echo "  Quiz: $QUIZ_PID"
echo "  Cloze: $CLOZE_PID"
echo "  Reasoning: $REASONING_PID"
echo "  Citations: $CITATIONS_PID"
echo "  Sources: $SOURCES_PID"
echo ""
echo "Monitor progress with:"
echo "  tail -f ../logs/chat.log"
echo "  tail -f ../logs/quiz.log"
echo "  tail -f ../logs/cloze.log"
echo "  tail -f ../logs/reasoning.log"
echo "  tail -f ../logs/citations.log"
echo "  tail -f ../logs/sources.log"
echo ""
echo "Wait for completion with:"
echo "  wait $CHAT_PID $QUIZ_PID $CLOZE_PID $REASONING_PID $CITATIONS_PID $SOURCES_PID"
echo ""

# Wait for all to complete
wait $CHAT_PID $QUIZ_PID $CLOZE_PID $REASONING_PID $CITATIONS_PID $SOURCES_PID

echo ""
echo "========================================================================"
echo "✅ ALL GENERATORS COMPLETED!"
echo "========================================================================"
echo ""
echo "Output files:"
ls -lh ../output/*.jsonl
echo ""
echo "Check logs for details:"
ls -lh ../logs/*.log
