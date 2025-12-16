import os
import re
import subprocess
import traceback
import requests
from glob import glob

# Path dasar
TOOLS_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.abspath(os.path.join(TOOLS_DIR, ".."))
UPLOAD_DIR = os.path.join(PROJECT_DIR, "uploads")
SCRIPTS_DIR = os.path.join(UPLOAD_DIR, "transkrip")

# Path whisper & model
WHISPER_PATH = os.path.join(PROJECT_DIR, "build", "whisper")
MODEL_PATH = os.path.join(PROJECT_DIR, "models", "ggml-small.bin")

def transkrip_audio(upload_file=None):
    """
    Jika upload_file diberikan, gunakan file tersebut.
    Jika tidak, ambil file .webm terbaru di folder uploads.
    """
    try:
        # === Tentukan file input ===
        if upload_file:
            filename = os.path.basename(upload_file.filename) if upload_file.filename else f"rekaman-{int(os.times()[4]*1000)}.webm"
            input_path = os.path.join(UPLOAD_DIR, filename)
            os.makedirs(os.path.dirname(input_path) or UPLOAD_DIR, exist_ok=True)
            with open(input_path, "wb") as f:
                f.write(upload_file.file.read())
        else:
            list_files = glob(os.path.join(UPLOAD_DIR, "*.webm"))
            if not list_files:
                return "[ERROR] Tidak ada file .webm di folder uploads"
            input_path = max(list_files, key=os.path.getmtime)

        # === Konversi ke WAV ===
        basename = os.path.splitext(os.path.basename(input_path))[0]
        wav_path = os.path.join(UPLOAD_DIR, f"{basename}.wav")
        txt_path = os.path.join(SCRIPTS_DIR, f"{basename}")

        ffmpeg_cmd = [
            "ffmpeg",
            "-i", input_path, 
            "-ar", "16000", 
            "-ac", "1", 
            "-y", wav_path
        ]
        subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # === Jalankan Whisper ===
        whisper_cmd = [
            WHISPER_PATH,
            "-f", wav_path,
            "--model", MODEL_PATH,
            "--language", "id",
            "--output-txt", "",
            "--output-file", txt_path
        ]

        result = subprocess.run(
            whisper_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # === Ambil hasil dari file output ===
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                teks_asli = f.read().strip()
        else:
            teks_asli = result.stdout.strip()

        if not teks_asli:
            return "[GAGAL] Whisper tidak menghasilkan teks apa pun."

        # === Bersihkan timestamp agar hasil rapi per baris ===
        baris_bersih = []
        for line in teks_asli.splitlines():
            clean_line = re.sub(r"\[\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}\.\d{3}\]\s*", "", line).strip()
            if clean_line:
                baris_bersih.append(clean_line)

        teks = "\n".join(baris_bersih)
        return teks

    except subprocess.CalledProcessError as cpe:
        traceback.print_exc()
        return f"[GAGAL] Kesalahan proses eksternal: {cpe.stderr.strip()}"
    except Exception as e:
        traceback.print_exc()
        return f"[GAGAL] {e}"
