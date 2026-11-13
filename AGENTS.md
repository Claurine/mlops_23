# Petunjuk Project

Project ini adalah website statis tanpa framework.

## Struktur

- `site/index.html` berisi struktur halaman.
- `site/styles.css` berisi seluruh tampilan responsif.
- `site/app.js` berisi interaksi browser.
- `Dockerfile` menggunakan Nginx Alpine.
- `docker-compose.yml` membuka website pada port 8080.

## Aturan perubahan

- Gunakan bahasa Indonesia pada UI.
- Pertahankan dukungan layar ponsel mulai 360 piksel.
- Jangan menambahkan framework atau dependency JavaScript.
- Jangan memasukkan API key atau credential ke repository.
- Setelah mengubah JavaScript, jalankan pemeriksaan sintaks.
- Setelah mengubah Docker, pastikan `docker compose config` valid.

## Perintah verifikasi

```bash
node --check site/app.js
docker compose config
docker compose up --build
```
