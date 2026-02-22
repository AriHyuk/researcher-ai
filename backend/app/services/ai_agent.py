import logging
import json
import asyncio
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

        # 3-Tier Model Strategy (Latest Gemini 3 Series)
        self.model_lite = "gemini-3-flash-preview"   # Lightning fast, low latency
        self.model_flash = "gemini-3-flash-preview"  # Pro-level reasoning at Flash speed
        self.model_pro = "gemini-3.1-pro-preview"    # Ultimate reasoning for Editor & Reflection

    async def _panggil_gemini_async(self, model, prompt, tools=None, response_schema=None):
        """Helper buat panggil API secara async."""
        config_dict = {
            "temperature": 0.3,
            "tools": tools,
        }
        if response_schema:
            config_dict["response_mime_type"] = "application/json"
            config_dict["response_schema"] = response_schema

        config = types.GenerateContentConfig(**config_dict)
        
        # Karena SDK genai mungkin belum semua async-native di wrapper-nya, 
        # kita bungkus pake run_in_executor jika perlu, tapi terbaru biasanya support.
        # Untuk demo ini kita pake sync call tapi dibungkus biar gak block event loop.
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
        )
        return response

    async def stream_sequential_research(self, topik: str, target_pembaca: str) -> AsyncGenerator[str, None]:
        """
        Main pipeline dengan generator streaming (SSE style).
        """
        try:
            yield json.dumps({"status": "researching", "message": "🕵️ Researcher sedang mencari data ilmiah..."}) + "\n"
            
            # STEP 1: RESEARCHER
            prompt_researcher = f"""
            PERAN: Academic Researcher Spesialis Jurnal Ilmiah.
            TOPIK: {topik}
            TUGAS: Cari sumber ilmiah valid (.ac.id/ .edu / .gov) via Google Search.
            OUTPUT: Harus dalam format JSON yang berisi lis sumber (penulis, tahun, judul, temuan) dan ringkasan data.
            """
            tools_grounding = [types.Tool(google_search=types.GoogleSearch())] if self.use_vertex else None
            
            res_research = await self._panggil_gemini_async(
                self.model_lite, 
                prompt_researcher, 
                tools=tools_grounding,
                response_schema=ResearcherOutput
            )
            
            research_data = ResearcherOutput.model_validate_json(res_research.text)
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
                res_editor = await self._panggil_gemini_async(self.model_pro, prompt_editor)
                
                if res_editor.text.startswith("REVISI:"):
                    feedback = res_editor.text
                    yield json.dumps({"status": "revising", "message": "⚠️ Editor minta revisi!", "feedback": feedback}) + "\n"
                    prompt_revisi = f"""
                    DRAFT SEBELUMNYA: {draft_content}
                    FEEDBACK EDITOR: {feedback}
                    TUGAS: Perbaiki draf.
                    """
                    res_writer = await self._panggil_gemini_async(self.model_flash, prompt_revisi)
                    draft_content = res_writer.text
                    yield json.dumps({"status": "writing_stream", "chunk": "[REVISED CONTENT GENERATED]"}) + "\n"
                else:
                    draft_content = res_editor.text
                    break

            # SAVE DATA
            await harvester.save_research(topik, draft_content, research_data.sources)
            
            yield json.dumps({
                "status": "completed", 
                "hasil_final": draft_content,
                "message": "🎉 Riset selesai dan data telah disimpan!"
            }) + "\n"

        except Exception as e:
            logger.error(f"Error in pipeline: {e}")
            yield json.dumps({"status": "error", "message": str(e)}) + "\n"
