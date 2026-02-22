# 🔑 Deep Dive: Dynamic Auth (Vertex AI vs Gemini API)

Salah satu fitur paling "Enterprise-Ready" di sini adalah **BYOK** (Bring Your Own Key).

## 1. Dua Dunia Gemini

- **Gemini API (Public/AI Studio):** Lebih gampang dipake buat personal, setup-nya simpel pake API Key.
- **Vertex AI (GCP):** Untuk skala perusahaan. Lebih aman, punya tata kelola data (governance), dan kuota lebih gede.

## 2. Implementasi di Code

Cek `backend/app/services/ai_agent.py`. Logika `__init__` nya cerdas:

```python
if gemini_api_key:
    # Pake SDK mode standar
    self.client = genai.Client(api_key=gemini_api_key)
else:
    # Pake mode Vertex AI
    self.client = genai.Client(vertexai=True, ...)
```

## 3. Strategi Deployment

- Pas abang deploy ke Cloud Run, abang gak perlu masukin Key Gemini (aman!). Sistem bakal otomatis pake *Service Account* Vertex AI.
- Tapi kalo temen abang mau pake aplikasi abang tapi dia mau bayar billing-nya sendiri, dia tinggal masukin Key dia di UI.

Ini namanya **Scalable Authentication Design**.
