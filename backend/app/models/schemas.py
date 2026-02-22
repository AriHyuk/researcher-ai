from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class JurnalRequest(BaseModel):
    topik: str = Field(..., example="Kecerdasan Buatan dalam Pendidikan")
    target_pembaca: str = Field("Dosen Penguji", example="Mahasiswa")

class ResearcherSource(BaseModel):
    penulis: str
    tahun: str
    judul: str
    temuan: str

class ResearcherOutput(BaseModel):
    topik: str
    sources: List[ResearcherSource]
    summary_data: str

class ResearchStep(BaseModel):
    riset_structured: ResearcherOutput
    draft_awal: str

class ResearchResponse(BaseModel):
    status: str
    tahapan: ResearchStep
    hasil_final: str
    sumber_html: Optional[str] = None
