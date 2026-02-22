from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    API untuk riset jurnal otomatis berbasis AI.
    Sistem ini menggunakan struktur **Sequential Multi-Agent** (Researcher -> Writer -> Editor)
    untuk menghasilkan draf akademik berkualitas tinggi dari sebuah topik.
    
    *Dibuat untuk keperluan riset dan pengembangan.*
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS logic: Jika origins contain '*', credentials harus False (Keamanan Browser)
origins = settings.ALLOWED_ORIGINS
if isinstance(origins, str):
    origins = [origins]

allow_all_origins = "*" in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Masukkan router
app.include_router(router, prefix="/api")

# Compat support untuk root endpoint di luar prefix /api jika dibutuhkan
@app.get("/")
async def health():
    return {"status": "OK", "app": settings.APP_NAME}
