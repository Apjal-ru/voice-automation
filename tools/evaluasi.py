import os
import json
from sklearn.metrics import accuracy_score, f1_score

TOOLS_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.abspath(os.path.join(TOOLS_DIR, ".."))
UPLOAD_DIR = os.path.join(PROJECT_DIR, "uploads")
PARSE_DIR = os.path.join(UPLOAD_DIR, "parse")
OUTPUT_DIR = os.path.join(UPLOAD_DIR, "evaluasi")

FIELDS = [
    "keluhan", "riwayat", "sosial",
    "tekananDarah", "nadi", "suhu",
    "frekuensiNafas", "beratBadan",
    "assesmen", "plan",
    "kepala", "mata", "tht", "leher",
    "paru", "jantung", "abdomen",
    "ekstermitas", "uro"
]

def is_filled(value):
    if value is None: return False
    # Tambahkan pengecekan jika value adalah list atau dict
    if isinstance(value, (list, dict)): return len(value) > 0
    val_str = str(value).strip().lower()
    return val_str not in ["-", "", "none", "null", "tidak ada", "normal"]

def main():
    y_true, y_pred = [], []
    skipped = 0

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for fname in os.listdir(PARSE_DIR):
        if not fname.endswith(".json") or fname.endswith(".gold.json"):
            continue

        base = fname.replace(".json", "")
        pred_path = os.path.join(PARSE_DIR, fname)
        gold_path = os.path.join(PARSE_DIR, base + ".gold.json")

        if not os.path.exists(gold_path):
            print(f"⚠️ GOLD tidak ditemukan untuk {fname}")
            skipped += 1
            continue

        with open(pred_path, encoding="utf-8") as f:
            pred = json.load(f)

        with open(gold_path, encoding="utf-8") as f:
            gold = json.load(f)

        for field in FIELDS:
            y_true.append(1 if gold.get(field, False) else 0)
            y_pred.append(1 if is_filled(pred.get(field, "")) else 0)

    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    result = {
        "total_sample": len(y_true),
        "accuracy": round(acc, 4),
        "f1_score": round(f1, 4),
        "skipped_files": skipped
    }

    outpath = os.path.join(OUTPUT_DIR, "hasil_evaluasi.json")
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n=== HASIL EVALUASI ===")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
