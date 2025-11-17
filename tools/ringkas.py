import requests
import json
import traceback
import os
import time
import secrets

# Alamat server Ollama remote
OLLAMA_HOST = "http://10.9.23.2:11434"

def ringkas_teks(teks, model="mistral:7b", source_filename=None):
    if not teks.strip():
        return "Tidak ada transkripsi yang terdeteksi"
    
    url = f"{OLLAMA_HOST}/api/generate"

    # =====================================================
    # Tambahan instruksi PE Normal/Abnormal
    # =====================================================
    payload = {
        "model": model,
        "prompt": f"""
Kamu adalah asisten medis, yang membantu dokter meringkas percakapan dengan pasien.
Gunakan format SOAP.

- Tugasmu adalah meringkas teks percakapan antara dokter dan pasien.
- Jangan berasumsi atau menambahkan informasi yang tidak ada dalam percakapan.
- Jika informasi tidak ada, isikan dengan tanda "-" tanpa keterangan tambahan.

Format ringkasan WAJIB seperti berikut:

Keluhan utama: ...
Riwayat penyakit: ...
Sosial Budaya: ...
Tekanan Darah: ...
Nadi: ...
Suhu: ...
Frekuensi Nafas: ...
Berat Badan: ...
Asesmen: ...
Plan: ...

Pemeriksaan Fisik (PE):
Kepala: Normal/Abnormal
Mata: Normal/Abnormal
THT: Normal/Abnormal
Leher: Normal/Abnormal
Paru: Normal/Abnormal
Jantung: Normal/Abnormal
Abdomen: Normal/Abnormal
Ekstermitas: Normal/Abnormal
Uro-genital: Normal/Abnormal

Fokuskan PE hanya pada status Normal/Abnormal tanpa keterangan tambahan.
Jika tidak ditemukan dalam percakapan, set default = "Normal".

Gunakan bahasa Indonesia profesional dan singkat.

Teks percakapan:
{teks}
"""
    }

    try:
        print("[INFO] Mengirim permintaan ringkasan ke Ollama...")
        response = requests.post(url, json=payload, stream=True, timeout=300)

        if response.status_code != 200:
            raise RuntimeError(f"Gagal merangkum teks: {response.text}")

        ringkasan = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        ringkasan += data["response"]
                except json.JSONDecodeError:
                    continue

        ringkasan = ringkasan.strip() if ringkasan else "Tidak ada balasan dari model."

        # Print hasil
        print("======================================================")
        print("[RESULT] Ringkasan dari Ollama:")
        print(ringkasan)
        print("======================================================")

        # Simpan ringkasan ke uploads/ringkasan
        try:
            tools_dir = os.path.dirname(__file__)
            project_dir = os.path.abspath(os.path.join(tools_dir, ".."))
            uploads_dir = os.path.join(project_dir, "uploads/ringkasan")
            os.makedirs(uploads_dir, exist_ok=True)

            if source_filename:
                base = os.path.splitext(os.path.basename(source_filename))[0]
                outname = f"{base}.txt"
                outpath = os.path.join(uploads_dir, outname)
                if os.path.exists(outpath):
                    timecode = f"{int(time.time()*1000)}-{secrets.token_hex(3)}"
                    outname = f"{base}-{timecode}.txt"
                    outpath = os.path.join(uploads_dir, outname)
            else:
                timecode = f"{int(time.time()*1000)}-{secrets.token_hex(3)}"
                outname = f"ringkasan-{timecode}.txt"
                outpath = os.path.join(uploads_dir, outname)

            with open(outpath, "w", encoding="utf-8") as of:
                of.write(ringkasan)

            print(f"[INFO] Ringkasan disimpan ke: {outpath}")
        except Exception as e:
            print("[WARN] Gagal menyimpan ringkasan:", e)

        return ringkasan

    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"Gagal menghubungi Ollama: {str(e)}")

def parse_ringkasan(ringkasan):

    # SOAP
    keluhan = ""
    riwayat = ""
    sosial = ""
    tekananDarah = ""
    nadi = ""
    suhu = ""
    frekuensiNafas = ""
    beratBadan = ""
    assesmen = ""
    plan = ""

    # PE
    kepala = "Normal"
    mata = "Normal"
    tht = "Normal"
    leher = "Normal"
    paru = "Normal"
    jantung = "Normal"
    abdomen = "Normal"
    ekstremitas = "Normal"
    uro = "Normal"

    for line in ringkasan.splitlines():

        # SOAP
        if "Keluhan utama" in line:
            keluhan = line.split(":", 1)[1].strip()
        elif "Riwayat penyakit" in line:
            riwayat = line.split(":", 1)[1].strip()
        elif "Sosial Budaya" in line:
            sosial = line.split(":", 1)[1].strip()
        elif "Tekanan Darah" in line:
            tekananDarah = line.split(":", 1)[1].strip()
        elif "Nadi" in line:
            nadi = line.split(":", 1)[1].strip()
        elif "Suhu" in line:
            suhu = line.split(":", 1)[1].strip()
        elif "Frekuensi Nafas" in line:
            frekuensiNafas = line.split(":", 1)[1].strip()
        elif "Berat Badan" in line:
            beratBadan = line.split(":", 1)[1].strip()
        elif "Asesmen" in line:
            assesmen = line.split(":", 1)[1].strip()
        elif "Plan" in line:
            plan = line.split(":", 1)[1].strip()

        # Pemeriksaan Fisik (PE)
        elif "Kepala" in line:
            kepala = line.split(":", 1)[1].strip()
        elif "Mata" in line:
            mata = line.split(":", 1)[1].strip()
        elif "THT" in line:
            tht = line.split(":", 1)[1].strip()
        elif "Leher" in line:
            leher = line.split(":", 1)[1].strip()
        elif "Paru" in line:
            paru = line.split(":", 1)[1].strip()
        elif "Jantung" in line:
            jantung = line.split(":", 1)[1].strip()
        elif "Abdomen" in line:
            abdomen = line.split(":", 1)[1].strip()
        elif "Ekstermitas" in line:
            ekstremitas = line.split(":", 1)[1].strip()
        elif "Uro-genital" in line or "Urogenital" in line or "Uro" in line:
            uro = line.split(":", 1)[1].strip()

    dataInput = {
        "keluhan": keluhan,
        "riwayat": riwayat,
        "sosial": sosial,
        "tekananDarah": tekananDarah,
        "nadi": nadi,
        "suhu": suhu,
        "frekuensiNafas": frekuensiNafas,
        "beratBadan": beratBadan,
        "assesmen": assesmen,
        "plan": plan,

        # Pemeriksaan fisik
        "kepala": kepala,
        "mata": mata,
        "tht": tht,
        "leher": leher,
        "paru": paru,
        "jantung": jantung,
        "abdomen": abdomen,
        "ekstermitas": ekstremitas,
        "uro": uro
    }

    return dataInput
