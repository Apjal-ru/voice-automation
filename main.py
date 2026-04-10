import os
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from tools.transkrip import transkrip_audio
from tools.ringkas import ringkas_teks, parse_ringkasan
from tools.isi_form import isi_form
import traceback


app = FastAPI()

# Static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Serve uploads directory (read-only)
app.mount("/uploads/parse", StaticFiles(directory="uploads/parse"), name="uploads")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("soap_global.html", {"request": request})

@app.get("/doctor/soap", response_class=HTMLResponse)
async def doctor_soap(request: Request):
    """Route baru untuk akses dokter ke formulir SOAP."""
    return templates.TemplateResponse("soap_global.html", {"request": request})
    

@app.post("/transkrip")
async def proses(file: UploadFile = File(...)):
    try:
        # 1. Transkripsi audio
        teks = transkrip_audio(file)

        if not teks:
            return JSONResponse({"error": "Tidak ada hasil transkripsi."}, status_code=400)

        if isinstance(teks, str) and (teks.startswith("[GAGAL]") or teks.startswith("[ERROR]")):
            return JSONResponse({"error": "Transkripsi gagal.", "detail": teks}, status_code=500)

        # 2. Ringkas dengan LLaMA
        source_fname = getattr(file, "filename", None)
        summary = ringkas_teks(teks, source_filename=source_fname)

        # 3. Parsing hasil ringkasan
        dataInput = parse_ringkasan(summary)

        # 4. Simpan form JSON
        form_filename = isi_form(dataInput, source_filename=source_fname)

        # 5. Return ke frontend (TERMASUK Pemeriksaan Fisik)
        return JSONResponse({
            "teks": teks,
            "summary": summary,

            "keluhan": dataInput.get("keluhan"),
            "riwayat": dataInput.get("riwayat"),
            "sosial": dataInput.get("sosial"),
            "tekananDarah": dataInput.get("tekananDarah"),
            "nadi": dataInput.get("nadi"),
            "suhu": dataInput.get("suhu"),
            "frekuensiNafas": dataInput.get("frekuensiNafas"),
            "beratBadan": dataInput.get("beratBadan"),
            "assesmen": dataInput.get("assesmen"),
            "plan": dataInput.get("plan"),

            # === Pemeriksaan Fisik (PE) ===
            "kepala": dataInput.get("kepala"),
            "mata": dataInput.get("mata"),
            "tht": dataInput.get("tht"),
            "leher": dataInput.get("leher"),
            "paru": dataInput.get("paru"),
            "jantung": dataInput.get("jantung"),
            "abdomen": dataInput.get("abdomen"),
            "ekstermitas": dataInput.get("ekstermitas"),
            "uro": dataInput.get("uro"),

            # file json untuk auto inject
            "form_file": form_filename
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)
