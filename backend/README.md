# Research API (Sequential Multi-Agent) 🚀

API berbasis **FastAPI** yang melakukan riset jurnal secara otomatis menggunakan **Google Gemini (Vertex AI)** dengan pendekatan *Sequential Multi-Agent*.

## 🛠️ Fitur Utama
- **Researcher:** Mencari sumber jurnal valid via Google Search Grounding.
- **Writer:** Menyusun narasi akademik dengan sitasi otomatis.
- **Editor:** Melakukan quality control pada tata bahasa dan validitas sumber.
- **Swagger UI:** Dokumentasi API interaktif dengan integrasi API Key.

---

## 🔑 Setup API Key

Project ini memiliki sistem pengamanan API Key sederhana untuk melindungi endpoint kamu.

### 1. Buat API Key
Karena API Key ini dibuat sendiri oleh kamu, kamu bisa generate string random apa saja. Pake command ini di terminal (Python) biar keren:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Pasang di `.env`
Salin file `.env.example` menjadi `.env` dan masukkan key yang baru kamu buat:
```env
GOOGLE_CLOUD_PROJECT=your-project-id
API_KEY=hasil-generate-tadi-disini
ALLOWED_ORIGINS=http://localhost:3000
```

---

## 🚀 Cara Menjalankan

### Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt pydantic-settings
   ```
2. Login ke Google Cloud (ADC):
   ```bash
   gcloud auth application-default login
   ```
3. Run server:
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

### Docker Compose (Lebih Simpel)
Jika ingin menjalankan dengan satu command tanpa ngetik manual:

```bash
docker-compose up --build
```

Aplikasi akan langsung jalan di port `8080` dan otomatis menggunakan variabel dari file `.env`.

---

## 📖 Dokumentasi API
Setelah server jalan, buka:
- **Swagger UI:** `http://localhost:8080/docs`
- **Redoc:** `http://localhost:8080/redoc`

*Klik tombol **"Authorize"** di Swagger UI dan masukkan API Key kamu untuk mencoba endpoint Research!*

---

## 🛡️ License
MIT License. Feel free to use and contribute!
