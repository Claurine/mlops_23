import json, os, re
from pathlib import Path
import lmstudio as lms

IMAGE = Path("data/raw/nota-sample.png")
MODEL = os.environ["LM_STUDIO_MODEL"]
image = lms.prepare_image(str(IMAGE))
model = lms.llm(MODEL)
chat = lms.Chat()
chat.add_user_message(
  "Baca nota. Ekstrak merchant, tanggal, item, subtotal, pajak, dan total. "
  "Keluarkan JSON valid. Jika pajak tidak terlihat, isi 0. Jangan mengarang.",
  images=[image],
)
prediction = model.respond(chat)

# Pembersihan Markdown & Ekstraksi Blok JSON
content = prediction.content.strip()

# Cari teks di dalam kurung kurawal { ... } jika model memberi teks pembuka
json_match = re.search(r'\{.*\}', content, re.DOTALL)
if json_match:
    content = json_match.group(0)

result = json.loads(content)
Path("reports/receipt.json").write_text(
  json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(json.dumps(result, indent=2, ensure_ascii=False))
