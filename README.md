# Hermes Agent OpenCode HTML Docker

Project pendamping untuk modul praktikum instalasi Hermes Agent dan OpenCode.

## Jalankan website

```bash
docker compose up --build
```

Buka `http://localhost:8080`.

## Hentikan website

```bash
docker compose down
```

## Verifikasi tanpa Docker

Sajikan folder `site` menggunakan server file sederhana:

```bash
python3 -m http.server 8000 --directory site
```

Buka `http://localhost:8000`.

## Alur agent

1. Instal Hermes Agent.
2. Instal OpenCode CLI.
3. Di OpenCode, jalankan `/models` dan pilih model yang bertanda Free.
4. Instal skill OpenCode pada Hermes:

```bash
hermes skills install official/autonomous-ai-agents/opencode
```

5. Jalankan Hermes dari folder project dan gunakan prompt pada `PROMPT.md`.

Model gratis OpenCode dapat berubah. Pilih model gratis yang tersedia saat praktikum, dan jangan mengunci nama model tertentu pada konfigurasi project.
