# 🧠 Deep Dive: Sequential Agent Orchestration

Project ini bukan sekadar "panggil API". Ada arsitektur cerdas dibaliknya yang disebut **Sequential Agentic Workflow**.

## 1. Konsep Multi-Agent

Kita membagi otak AI menjadi 3 peran berbeda (Separation of Concerns):

- **Researcher:** Fokus pada akurasi data dan grounding (Google Search). Dia "mata" sistem.
- **Writer:** Fokus pada bahasa dan narasi. Dia "mulut" sistem.
- **Editor:** Fokus pada kritik dan kualitas. Dia "filter" sistem.

## 2. Strategi 3-Tier Model

Kenapa pake model beda-beda?
- **Efficiency:** `Gemini 3 Flash` sangat murah dan cepat. Cocok buat cari data atau nulis draf awal.
- **Sophistication:** `Gemini 3.1 Pro` punya nalar (reasoning) yang kuat. Kita pake dia buat **Editor** karena tugasnya mengkritik, bukan cuma nulis.

## 3. Reflection Loop (Self-Correction)

Ini fitur "sakti" yang bikin output makin pro.

1. Editor nerima draf dari Writer.
2. Editor nge-cek: "Ini drafnya sampah gak? Akurat gak?"
3. Kalo kurang, Editor kasih instruksi **REVISI**.
4. Loop ini diulang (di project ini max 2x) sampe Editor bilang "OK".
5. Teknik ini disebut *Agentic Reasoning Pattern*.

## 4. Tips Belajar Lebih Lanjut

- Baca paper tentang "Agentic Workflows" oleh Andrew Ng.
- Pelajari "Prompt Chaining" vs "Agent Iteration".
