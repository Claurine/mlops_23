import base64
import io
import json
import os
from datetime import date
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from openai import AsyncOpenAI
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="Receipt Finance API", version="1.0.0")

client = AsyncOpenAI(
    base_url=os.getenv("MODEL_BASE_URL", "http://127.0.0.1:1234/v1"),
    api_key=os.getenv("MODEL_API_KEY", "lm-studio"),
    timeout=120.0,
)

MODEL_NAME = os.getenv("MODEL_NAME", "")
MAX_BYTES = int(os.getenv("MAX_FILE_MB", "8")) * 1024 * 1024


class ReceiptItem(BaseModel):
    name: str
    quantity: Optional[float] = 1.0
    unit_price: Optional[float] = None
    subtotal: Optional[float] = None


class ReceiptData(BaseModel):
    merchant: Optional[str] = None
    transaction_date: Optional[str] = None
    currency: Optional[str] = "IDR"
    items: list[ReceiptItem] = Field(default_factory=list)
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    discount: Optional[float] = None
    total: Optional[float] = None
    payment_method: Optional[str] = None


class ReceiptResponse(BaseModel):
    success: bool
    data: ReceiptData
    metadata: dict


@app.get("/health")
async def health():
    return {"status": "ok"}


def clean_number(val):
    """Membersihkan nilai angka dari string seperti 'Rp 70.000', '1 lusin', 'x2' dll."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        import re

        cleaned = re.sub(r"[^\d.,-]", "", val)
        if not cleaned:
            return None
        if "." in cleaned and "," in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        elif "." in cleaned:
            parts = cleaned.split(".")
            if len(parts) > 1 and len(parts[-1]) == 3:
                cleaned = "".join(parts)
        elif "," in cleaned:
            parts = cleaned.split(",")
            if len(parts) > 1 and len(parts[-1]) == 3:
                cleaned = "".join(parts)

        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


@app.post("/api/receipts/extract", response_model=ReceiptResponse)
async def extract_receipt(file: UploadFile = File(...)):
    if not MODEL_NAME:
        raise HTTPException(500, "MODEL_NAME belum dikonfigurasi")

    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(415, "Format gambar tidak didukung")

    raw = await file.read(MAX_BYTES + 1)
    if not raw or len(raw) > MAX_BYTES:
        raise HTTPException(413, "Gambar kosong atau melebihi batas ukuran")

    try:
        image = Image.open(io.BytesIO(raw))
        image.verify()
        image = Image.open(io.BytesIO(raw))
        if image.format not in {"JPEG", "PNG", "WEBP"}:
            raise HTTPException(415, "Format gambar tidak didukung")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(400, "Berkas bukan gambar yang valid")

    mime = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "WEBP": "image/webp",
    }[image.format]

    encoded = base64.b64encode(raw).decode("ascii")
    image_url = f"data:{mime};base64,{encoded}"

    prompt = """
    Ekstrak data nota keuangan dari gambar.
    Kembalikan SATU objek JSON valid dengan struktur:
    {
      "merchant": string atau null,
      "transaction_date": "YYYY-MM-DD" atau null,
      "currency": "IDR",
      "items": [
        {
          "name": string,
          "quantity": float angka murni (contoh: 1),
          "unit_price": float angka murni (contoh: 36000),
          "subtotal": float angka murni
        }
      ],
      "subtotal": float atau null,
      "tax": float atau null,
      "discount": float atau null,
      "total": float atau null,
      "payment_method": string atau null
    }

    Catatan: Hapus semua tulisan 'Rp', 'lusin', 'ml', titik/koma ribuan dari nilai numerik.
    """

    try:
        result = await client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                    ],
                }
            ],
        )

        content = result.choices[0].message.content
        if not content:
            raise ValueError("Output model kosong")

        start = content.find("{")
        end = content.rfind("}")
        if start < 0 or end < start:
            raise ValueError("JSON tidak ditemukan")

        payload = json.loads(content[start : end + 1])

        if isinstance(payload, dict):
            if not payload.get("currency"):
                payload["currency"] = "IDR"

            for key in ["subtotal", "tax", "discount", "total"]:
                if key in payload:
                    payload[key] = clean_number(payload[key])

            if "items" in payload and isinstance(payload["items"], list):
                for item in payload["items"]:
                    if isinstance(item, dict):
                        item["quantity"] = (
                            clean_number(item.get("quantity")) or 1.0
                        )
                        item["unit_price"] = clean_number(item.get("unit_price"))
                        item["subtotal"] = clean_number(item.get("subtotal"))

        data = ReceiptData.model_validate(payload)

        return ReceiptResponse(
            success=True,
            data=data,
            metadata={
                "model": MODEL_NAME,
                "processing_status": "success",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            502, f"Inferensi gagal atau output model tidak valid: {str(e)}"
        )
    finally:
        await file.close()
