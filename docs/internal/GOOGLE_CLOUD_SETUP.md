# ☁️ Google Cloud & ADC Setup Guide

Dokumen ini menjelaskan cara kerja autentikasi Google Cloud di project ini guna menghindari error "Credential not found" atau "Project mismatch".

## 1. Apa itu Application Default Credentials (ADC)?

ADC adalah standar Google untuk mencari kredensial secara otomatis dalam lingkungan pengembangan. Saat abang jalanin:

```powershell
gcloud auth application-default login
```

Google bakal bikin file JSON di:
`%APPDATA%\gcloud\application_default_credentials.json` (Windows)

**PENTING:** Project ini menggunakan file tersebut di dalam Docker dengan cara **Volume Mounting** di `docker-compose.yml`:

```yaml
volumes:
  - ${APPDATA}/gcloud/application_default_credentials.json:/root/.config/gcloud/application_default_credentials.json:ro
```
Ini alasan kenapa abang gak perlu masukin API Key manual kalo udah login di laptop.

## 2. Mengelola Project ID

Seringkali kita punya banyak project di GCP. Pastikan project yang aktif di terminal sama dengan yang di `.env`.

**Cek Project Aktif:**

```powershell
gcloud config get-value project
```

**Ganti Project Aktif:**

```powershell
gcloud config set project [PROJECT_ID_ABANG]
```

## 3. Sinkronisasi Port (8081)

Karena port `8080` sering dipake service Windows lain, kita pindah ke `8081`. 3 tempat ini harus SAMA:
- `docker-compose.yml`: `8081:8080`
- `backend/.env`: `ALLOWED_ORIGINS` (buat CORS)
- `frontend/.env`: `VITE_API_BASE_URL=http://localhost:8081`

## 4. Tips Debugging Cepat

Kalo Agent tiba-tiba gak respon atau "Failed to fetch":

1. **Cek Login:** Re-run `gcloud auth application-default login`.
2. **Cek Docker:** `make down` terus `make up` buat refresh mounting file kredensial.
3. **Cek Log:** `docker logs ai-researcher-api-1` buat liat error asli dari Python.

### 📝 Final Note

---
*Dibuat untuk mencatat lesson learned - ai-researcher V2.1.1*
