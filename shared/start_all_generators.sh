#!/bin/bash

echo "🚀 Starting ALL Gap Filling Generators"
echo "======================================"
echo ""

# Launch v2.6 (Tone Flexibility)
echo "📝 Launching v2.6 Tone Flexibility Generator..."
python3 generator_v2.6_tone_flexibility.py > logs/v2.6_output.log 2>&1 &
PID1=$!
echo "   PID: $PID1"

# Launch v2.5 (Emotional Support)  
echo "💙 Launching v2.5 Emotional Support Generator..."
python3 generator_v2.5_emotional_support.py > logs/v2.5_output.log 2>&1 &
PID2=$!
echo "   PID: $PID2"

# Launch v2.7 (Humanities + Soft Skills)
echo "📚 Launching v2.7 Humanities + Soft Skills Generator..."
python3 generator_v2.7_humanities_softskills.py > logs/v2.7_output.log 2>&1 &
PID3=$!
echo "   PID: $PID3"

echo ""
echo "✅ ALL 3 GENERATORS LAUNCHED!"
echo ""
echo "PIDs: $PID1 (v2.6), $PID2 (v2.5), $PID3 (v2.7)"
echo ""
echo "Monitor with:"
echo "  tail -f logs/v2.6_output.log"
echo "  tail -f logs/v2.5_output.log"
echo "  tail -f logs/v2.7_output.log"
echo ""
echo "Check progress:"
echo "  watch -n 5 'wc -l output/*.jsonl'"
