import os
import json
import re

TOOLS_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.abspath(os.path.join(TOOLS_DIR, ".."))
UPLOAD_DIR = os.path.join(PROJECT_DIR, "uploads")
TRANSKRIP_DIR = os.path.join(UPLOAD_DIR, "transkrip")
PARSE_DIR = os.path.join(UPLOAD_DIR, "parse")

FIELDS_KEYWORDS = {
    "keluhan": ["nyeri", "sakit", "keluhan", "mengeluh"],
    "riwayat": ["riwayat", "sebelumnya", "pernah"],
    "sosial": ["merokok", "alkohol", "pekerjaan"],
    "tekananDarah": ["tekanan darah", "mmhg"],
    "nadi": ["nadi", "denyut"],
    "suhu": ["suhu", "demam"],
    "frekuensiNafas": ["nafas", "respirasi"],
    "beratBadan": ["berat badan", "kg"],
    "assesmen": ["diagnosis", "kesan", "asesmen"],
    "plan": ["rencana", "terapi", "obat"],

    # Pemeriksaan Fisik
    "kepala": ["kepala"],
    "mata": ["mata"],
    "tht": ["telinga", "hidung", "tenggorokan"],
    "leher": ["leher"],
    "paru": ["paru", "napas"],
    "jantung": ["jantung"],
    "abdomen": ["perut", "abdomen"],
    "ekstermitas": ["tangan", "kaki"],
    "uro": ["kemih", "urin", "urogenital"]
}

def detect_field(text, keywords):
    text = text.lower()
    return any(re.search(rf"\b{k}\b", text) for k in keywords)

def main():
    os.makedirs(PARSE_DIR, exist_ok=True)

    for fname in os.listdir(TRANSKRIP_DIR):
        if not fname.endswith(".txt"):
            continue

        # 🔧 BASE NAME TANPA EXT
        base = fname.replace(".txt", "")

        # 🔧 TAMBAHKAN PREFIX form-
        gold_name = f"form-{base}.gold.json"
        gold_path = os.path.join(PARSE_DIR, gold_name)

        if os.path.exists(gold_path):
            continue

        with open(os.path.join(TRANSKRIP_DIR, fname), encoding="utf-8") as f:
            text = f.read()

        gold = {}
        for field, keywords in FIELDS_KEYWORDS.items():
            gold[field] = detect_field(text, keywords)

        with open(gold_path, "w", encoding="utf-8") as f:
            json.dump(gold, f, indent=2)

        print(f"✅ GOLD dibuat: {gold_name}")

if __name__ == "__main__":
    main()
