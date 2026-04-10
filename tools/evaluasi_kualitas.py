import os
import torch
import json
import math
from transformers import AutoModelForCausalLM, AutoTokenizer
from evaluate import load

# Konfigurasi Folder
TOOLS_DIR = os.path.dirname(__file__)
TRANSKRIP_DIR = os.path.join(TOOLS_DIR, "..", "uploads", "transkrip")
OUTPUT_DIR = os.path.join(TOOLS_DIR, "..", "uploads", "evaluasi")
OLLAMA_HOST = "http://10.9.23.205:11434/api/generate"
# Load Models (Llama 3.2 untuk Perplexity & Toxicity evaluator)
device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "/home/afzal/models/Llama-3.2" # Sesuaikan dengan model lokal Anda

print("Loading models for evaluation...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")
toxicity_scorer = load("toxicity", sample_threshold=0.3)

def get_metrics(text):
    # 1. Hitung Perplexity
    inputs = tokenizer(text, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss
        ppl = math.exp(loss.item())

    # 2. Hitung Toxicity
    tox_results = toxicity_scorer.compute(predictions=[text])
    tox_score = tox_results["toxicity"][0]
    
    return ppl, tox_score

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results = []
    
    files = [f for f in os.listdir(TRANSKRIP_DIR) if f.endswith(".txt")]
    print(f"Memulai evaluasi pada {len(files)} file...")

    for fname in files:
        with open(os.path.join(TRANSKRIP_DIR, fname), 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content.strip()) < 5: continue
            
            ppl, tox = get_metrics(content)
            results.append({
                "file": fname,
                "perplexity": round(ppl, 2),
                "toxicity": round(tox, 5)
            })
            print(f"Processed {fname} | PPL: {round(ppl,2)} | Tox: {round(tox,5)}")

    # Hitung Rata-rata
    avg_ppl = sum(d['perplexity'] for d in results) / len(results)
    avg_tox = sum(d['toxicity'] for d in results) / len(results)

    final_report = {
        "summary": {
            "total_files": len(results),
            "average_perplexity": round(avg_ppl, 2),
            "average_toxicity": round(avg_tox, 5)
        },
        "details": results
    }

    with open(os.path.join(OUTPUT_DIR, "kualitas_bahasa.json"), "w") as f:
        json.dump(final_report, f, indent=2)
    
    print("\n=== EVALUASI SELESAI ===")
    print(f"Rata-rata Perplexity: {round(avg_ppl, 2)}")
    print(f"Rata-rata Toxicity: {round(avg_tox, 5)}")

if __name__ == "__main__":
    main()