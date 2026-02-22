# 📝 Changelog // ai-researcher

Semua update besar, perbaikan bug, dan perubahan arsitektur dicatat di sini.

## [V2.1.1] - 2026-02-22

### Fixed
- **Port Conflict Fix:** Backend port di-shift dari `8080` ke `8081` untuk menghindari bentrokan dengan service sistem lain.
- **Missing Variables:** Menambahkan `.env` default untuk backend & frontend agar `docker-compose` tidak jalan pincang.
- **Improved Build:** Konfigurasi `node_modules` di Docker sekarang lebih isolatif untuk mencegah error copy file.
- **Internal Knowledge:** Update `AGENT.md` dengan context absolut project versi 2.1.

## [V2.1.0] - 2026-02-22

### Added
- **Internal Docs:** Menambahkan modul edukasi di `docs/internal/` (Agent Orchestration, Streaming SSE, dan Dynamic Auth).
- **Project Hygiene:** Implementasi `.gitignore` dan `.dockerignore` untuk root, backend, dan frontend.

### Fixed
- **Docker Build Error:** Memperbaiki error `cannot copy to non-directory` di frontend.

## [V2.0.0] - 2026-02-22

### Added
- **Sequential Multi-Agent V2:** Refactor total backend ke Async & Streaming API.
- **BYOK Support:** Fitur "Bring Your Own Key" (Gemini API Key).
- **Streaming UI:** UI baru berbasis React yang bisa baca stream SSE.
- **Makefile & Deploy Script:** Otomatisasi pengerjaan lokal dan deployment.
