import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class DataHarvester:
    def __init__(self, storage_path: str = "data/harvester"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def save_research(self, topic: str, result: str, sources: list):
        """
        Simpan hasil riset ke file JSONL.
        """
        try:
            filename = f"research_log_{datetime.now().strftime('%Y%m')}.jsonl"
            file_path = self.storage_path / filename
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "sources_count": len(sources),
                "sources": sources,
                "final_report": result
            }
            
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
            
            logger.info(f"📁 Data riset '{topic}' berhasil dipanen ke {filename}")
        except Exception as e:
            logger.error(f"❌ Gagal memanen data riset: {e}")

harvester = DataHarvester()
