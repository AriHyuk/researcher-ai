# 📡 Deep Dive: Streaming with Server-Sent Events (SSE)

Kenapa kita gak pake REST API biasa (Request-Response)? Karena proses AI itu lama (bisa 30-60 detik). Kalo pake REST biasa, user bakal liat layar loading bosenin.

## 1. Apa itu SSE?
SSE adalah standard komunikasi satu arah dari server ke client. Berbeda dengan Websocket yang dua arah dan berat, SSE jauh lebih ringan karena berjalan di atas protokol HTTP biasa.

## 2. Cara Kerja di Sini
1. **Backend (FastAPI):** Menggunakan `StreamingResponse`. Kita pake kata kunci `yield` di Python buat "nyicil" data ke client line-per-line.
2. **Frontend (React):** Menggunakan `fetch` API dengan `ReadableStream`. Kita baca data per chunk, di-decode, lalu di-parse jadi JSON.

## 3. Format Data (JSONL style)
Kita kirim data dalam format JSON setiap baris (Line-delimited JSON). Setiap baris punya `status` beda-beda:
- `researching`: Update pesan progres.
- `writing_stream`: Hasil ketikan real-time dari Writer.
- `completed`: Sinyal kalau proses udah beres.

## 4. Keuntungan Portofolio
Menunjukkan abang paham **Asynchronous Programming** dan **Real-time UX**, yang merupakan skill wajib Senior Front-end & Full-stack Engineer.
