import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class DataHarvester:
    def __init__(self, storage_path: str = "data/harvester"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def save_research(self, topic: str, result: str, sources: list, pipeline_metrics: dict = None):
        """
        Simpan hasil riset ke file JSONL.
        
        Sekarang dual-purpose:
        1. Dataset fine-tuning: topic → final_report
        2. Observability: latency, token usage, finish_reason per agen
        """
        try:
            filename = f"research_log_{datetime.now().strftime('%Y%m')}.jsonl"
            file_path = self.storage_path / filename

            # Hitung estimasi biaya berdasarkan token (harga Gemini 2.5, per 1M token)
            # Flash Lite: $0.1/1M input, $0.4/1M output | Flash: $0.3/1M | Pro: $1.25/1M
            cost_estimate_usd = 0.0
            if pipeline_metrics:
                researcher = pipeline_metrics.get("researcher", {})
                editor = pipeline_metrics.get("editor", {})
                # Researcher pakai model_lite
                cost_estimate_usd += ((researcher.get("tokens_in") or 0) * 0.10 / 1_000_000)
                cost_estimate_usd += ((researcher.get("tokens_out") or 0) * 0.40 / 1_000_000)
                # Editor pakai model_pro
                cost_estimate_usd += ((editor.get("total_tokens") or 0) * 1.25 / 1_000_000)

            data = {
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "sources_count": len(sources),
                "sources": [s.model_dump() if hasattr(s, 'model_dump') else s for s in sources],
                "final_report": result,
                # Observability metadata
                "observability": {
                    "pipeline_metrics": pipeline_metrics or {},
                    "cost_estimate_usd": round(cost_estimate_usd, 6),
                }
            }
            
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
            logger.info(
                f"📁 Data riset '{topic}' dipanen ke {filename} | "
                f"est. cost: ${cost_estimate_usd:.6f}"
            )
        except Exception as e:
            logger.error(f"❌ Gagal memanen data riset: {e}")

harvester = DataHarvester()
