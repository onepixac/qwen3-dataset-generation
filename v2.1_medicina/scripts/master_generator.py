"""
Master Generator for v2.0 Dataset (175K examples)
Orchestrates all generation tasks:
- 25K quiz (diritto 15K + economia 5K + cultura 5K)
- 10K cloze
- 10K reasoning  
- 10K citations
- 10K function calling
- 10K sample from temp datasets
- 95K from v1.0
"""

import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

class MasterGenerator:
    def __init__(self):
        self.base_dir = Path("/home/ec2-user/all1e/qwen3-4b-chat-rag-finetuning/v2_dataset_generation")
        self.output_dir = self.base_dir / "output"
        self.logs_dir = self.base_dir / "logs"
        
        self.start_time = datetime.now()
        self.log_file = self.logs_dir / f"master_generation_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        
    def log(self, message: str):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def run_step(self, step_name: str, script_path: str, timeout: int = 36000):
        """Run a generation step"""
        self.log(f"\n{'='*80}")
        self.log(f"🚀 Starting: {step_name}")
        self.log(f"{'='*80}")
        
        start = time.time()
        
        try:
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            elapsed = time.time() - start
            
            if result.returncode == 0:
                self.log(f"✅ {step_name} completed in {elapsed/60:.1f} minutes")
                self.log(f"   Output: {result.stdout[-500:]}")  # Last 500 chars
                return True
            else:
                self.log(f"❌ {step_name} failed!")
                self.log(f"   Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"⏱️ {step_name} timeout after {timeout/60:.1f} minutes")
            return False
        except Exception as e:
            self.log(f"❌ {step_name} error: {str(e)}")
            return False
    
    def generate_all(self):
        """Run all generation steps"""
        
        self.log("="*80)
        self.log("🚀 MASTER GENERATOR v2.0 - START")
        self.log("="*80)
        self.log(f"Start time: {self.start_time}")
        self.log(f"Log file: {self.log_file}")
        
        steps = [
            {
                "name": "QUIZ Generation (25K: diritto 15K + economia 5K + cultura 5K)",
                "script": str(self.base_dir / "quiz_generator.py"),
                "timeout": 18000  # 5 hours
            }
            # More steps will be added as we create them
        ]
        
        results = {}
        
        for step in steps:
            success = self.run_step(step["name"], step["script"], step["timeout"])
            results[step["name"]] = success
            
            if not success:
                self.log(f"⚠️ Step failed but continuing...")
        
        # Summary
        self.log("\n" + "="*80)
        self.log("📊 GENERATION SUMMARY")
        self.log("="*80)
        
        for step_name, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            self.log(f"{status}: {step_name}")
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        self.log(f"\nTotal generation time: {total_time/3600:.2f} hours")
        
        self.log("\n" + "="*80)
        self.log("🎉 MASTER GENERATION COMPLETE")
        self.log("="*80)

if __name__ == "__main__":
    generator = MasterGenerator()
    generator.generate_all()
