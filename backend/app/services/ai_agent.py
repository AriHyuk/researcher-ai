import logging
import json
import asyncio
import time
from typing import AsyncGenerator
from google import genai
from google.genai import types
from app.core.config import settings
from app.models.schemas import ResearcherOutput, ResearcherSource
from app.services.harvester import harvester

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchAgent:
    def __init__(self, gemini_api_key: str = None):
        """
        Inisialisasi Client secara dinamis.
        - Jika gemini_api_key ada -> Pake Gemini API (Public)
        - Jika kosong -> Pake Vertex AI (GCP Managed)
        """
        if gemini_api_key:
            logger.info("🔑 Menggunakan Gemini API Key (BYOK Mode)")
            self.client = genai.Client(api_key=gemini_api_key)
            self.use_vertex = False
        else:
            logger.info("☁️ Menggunakan Vertex AI (System Mode)")
            self.client = genai.Client(
                vertexai=True, 
                project=settings.GOOGLE_CLOUD_PROJECT, 
                location=settings.LOCATION
            )
            self.use_vertex = True

        # 3-Tier Model Strategy (Latest Gemini 2.5 Series - Specs Sept 2025)
        self.model_lite = "gemini-2.5-flash-lite"  # Ultra fast & budget friendly
        self.model_flash = "gemini-2.5-flash"       # Flagship price-performance
        self.model_pro = "gemini-2.5-pro"           # Most advanced for reasoning

    async def _panggil_gemini_async(self, model, prompt, tools=None, response_schema=None):
        """Helper buat panggil API secara async, sekaligus capture observability metrics."""
        config_dict = {
            "temperature": 0.3,
            "tools": tools,
        }
        if response_schema:
            config_dict["response_mime_type"] = "application/json"
            config_dict["response_schema"] = response_schema

        config = types.GenerateContentConfig(**config_dict)
        
        loop = asyncio.get_event_loop()
        t_start = time.perf_counter()
        response = await loop.run_in_executor(
            None, 
            lambda: self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
        )
        latency_ms = round((time.perf_counter() - t_start) * 1000)

        # Ambil usage metadata — ini yang biasanya dibuang
        usage = response.usage_metadata
        finish_reason = str(response.candidates[0].finish_reason) if response.candidates else "UNKNOWN"

        metrics = {
            "model": model,
            "latency_ms": latency_ms,
            "tokens_in": usage.prompt_token_count if usage else None,
            "tokens_out": usage.candidates_token_count if usage else None,
            "tokens_total": usage.total_token_count if usage else None,
            "finish_reason": finish_reason,
        }
        logger.info(f"📊 [{model}] latency={latency_ms}ms | tokens={metrics['tokens_total']} | finish={finish_reason}")

        return response, metrics

    async def stream_sequential_research(self, topik: str, target_pembaca: str) -> AsyncGenerator[str, None]:
        """
        Main pipeline dengan generator streaming (SSE style).
        """
        # Kumpulkan metrics tiap agen untuk disimpan ke harvester
        pipeline_metrics = {}

        try:
            yield json.dumps({"status": "researching", "message": "🕵️ Researcher sedang mencari data ilmiah..."}) + "\n"
            
            # STEP 1: RESEARCHER
            prompt_researcher = f"""
Kamu adalah Academic Researcher. Cari sumber ilmiah valid untuk topik berikut: "{topik}"
Gunakan Google Search untuk menemukan jurnal, paper, atau artikel dari domain .ac.id, .edu, atau .gov.

Setelah riset, buat OUTPUT HANYA BERUPA JSON MURNI (tanpa markdown, tanpa ``` blok) dengan format PERSIS seperti ini:
{{
  "topik": "{topik}",
  "sources": [
    {{
      "penulis": "Nama Penulis",
      "tahun": "2024",
      "judul": "Judul Paper",
      "temuan": "Temuan utama dari paper ini"
    }}
  ],
  "summary_data": "Ringkasan singkat dari semua temuan riset."
}}

PENTING: Output harus LANGSUNG JSON, tidak ada teks lain sebelum atau sesudah tanda kurung kurawal pertama.
            """
            tools_grounding = [types.Tool(google_search=types.GoogleSearch())] if self.use_vertex else None
            
            res_research, metrics_researcher = await self._panggil_gemini_async(
                self.model_lite, 
                prompt_researcher, 
                tools=tools_grounding
            )
            pipeline_metrics["researcher"] = metrics_researcher
            
            # Bersihkan output dari markdown code blocks jika ada
            raw_text = res_research.text.strip() if res_research.text else ""
            
            # Jika output kosong, buat fallback data
            if not raw_text:
                logger.warning("Researcher return empty response, using fallback data")
                raw_text = f'{{"topik": "{topik}", "sources": [{{"penulis": "AI", "tahun": "2025", "judul": "Riset tentang {topik}", "temuan": "Data tidak tersedia dari sumber eksternal."}}], "summary_data": "Riset dilakukan berdasarkan pengetahuan internal AI karena tidak ada akses ke sumber eksternal."}}'
            
            # Strip markdown code blocks
            if "```json" in raw_text:
                raw_text = raw_text.split("```json", 1)[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```", 1)[1].split("```")[0].strip()
            
            # Ambil substring JSON valid (dari { pertama ke } terakhir)
            if raw_text and not raw_text.startswith("{"):
                start = raw_text.find("{")
                if start != -1:
                    raw_text = raw_text[start:]
                    
            try:
                research_data = ResearcherOutput.model_validate_json(raw_text)
            except Exception as parse_err:
                logger.error(f"Parsing error: {parse_err}, raw: {raw_text[:200]}")
                # Parsing fallback jika field tidak sesuai
                research_data = ResearcherOutput(
                    topik=topik,
                    sources=[ResearcherSource(penulis="AI", tahun="2025", judul=f"Riset: {topik}", temuan="Tidak ada sumber yang bisa diparser.")],
                    summary_data=raw_text[:500] if raw_text else "Tidak ada data"
                )
                
            yield json.dumps({
                "status": "research_done", 
                "data": research_data.model_dump(),
                "message": "✅ Data riset berhasil dikumpulkan."
            }) + "\n"

            # STEP 2: WRITER
            yield json.dumps({"status": "writing", "message": "✍️ Writer sedang menyusun draf akademik..."}) + "\n"
            prompt_writer = f"""
            PERAN: Academic Writer.
            DATA RISET: {research_data.model_dump_json()}
            TARGET PEMBACA: {target_pembaca}
            TUGAS: Buat narasi akademik yang mengalir dengan sitasi otomatis (Markdown).
            """
            
            # Streaming Content Generation untuk Writer
            config = types.GenerateContentConfig(temperature=0.7)
            stream = self.client.models.generate_content_stream(
                model=self.model_flash,
                contents=prompt_writer,
                config=config
            )
            
            full_draft = ""
            for chunk in stream:
                full_draft += chunk.text
                yield json.dumps({"status": "writing_stream", "chunk": chunk.text}) + "\n"
            
            # STEP 3: EDITOR (Reflection Loop)
            yield json.dumps({"status": "editing", "message": "🧐 Editor sedang melakukan Quality Control..."}) + "\n"
            
            draft_content = full_draft
            revision_loops = 0
            editor_metrics_list = []

            for i in range(2):
                yield json.dumps({"status": "editing", "message": f"🔄 Reflection Loop ke-{i+1}..."}) + "\n"
                prompt_editor = f"""
                PERAN: Senior Editor.
                TOPIK: {topik}
                DRAFT: {draft_content}
                TUGAS: 
                1. Evaluasi draf. Apakah formal dan akurat?
                2. Jika SUDAH BAGUS, balas hanya dengan naskah final.
                3. Jika MASIH KURANG, awali dengan 'REVISI:' lalu feedback detail.
                """
                res_editor, metrics_editor = await self._panggil_gemini_async(self.model_pro, prompt_editor)
                editor_metrics_list.append(metrics_editor)
                
                if res_editor.text.startswith("REVISI:"):
                    revision_loops += 1
                    feedback = res_editor.text
                    yield json.dumps({"status": "revising", "message": "⚠️ Editor minta revisi!", "feedback": feedback}) + "\n"
                    prompt_revisi = f"""
                    DRAFT SEBELUMNYA: {draft_content}
                    FEEDBACK EDITOR: {feedback}
                    TUGAS: Perbaiki draf.
                    """
                    # Stream hasil revisi ke frontend (bukan placeholder)
                    config_revisi = types.GenerateContentConfig(temperature=0.7)
                    stream_revisi = self.client.models.generate_content_stream(
                        model=self.model_flash,
                        contents=prompt_revisi,
                        config=config_revisi
                    )
                    draft_content = ""
                    for chunk in stream_revisi:
                        draft_content += chunk.text
                        yield json.dumps({"status": "writing_stream", "chunk": chunk.text}) + "\n"
                else:
                    draft_content = res_editor.text
                    break

            # Aggregasi metrics editor — ambil total token & latency
            pipeline_metrics["editor"] = {
                "model": self.model_pro,
                "revision_loops": revision_loops,
                "total_latency_ms": sum(m["latency_ms"] for m in editor_metrics_list),
                "total_tokens": sum(m["tokens_total"] or 0 for m in editor_metrics_list),
                "finish_reasons": [m["finish_reason"] for m in editor_metrics_list],
            }

            # SAVE DATA (termasuk pipeline metrics untuk observability)
            await harvester.save_research(topik, draft_content, research_data.sources, pipeline_metrics)
            
            yield json.dumps({
                "status": "completed", 
                "hasil_final": draft_content,
                "message": "🎉 Riset selesai dan data telah disimpan!"
            }) + "\n"

        except Exception as e:
            logger.error(f"Error in pipeline: {e}")
            yield json.dumps({"status": "error", "message": str(e)}) + "\n"
