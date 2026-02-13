"""
Export current rejection reasons from the database to app/data/rejection_reasons_seed.json.

Run: python -m app.scripts.export_rejection_reasons

Commit the updated file to git so others get these values when they install locally.
"""

import json
import sys
from pathlib import Path

# Ensure project root is on path (for running as script or -m)
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from app.database import SessionLocal, SEED_FILE
from app.models import RejectionReasonMaster

_STAGES = ["moisture", "start", "mid", "90", "end"]


def main():
    db = SessionLocal()
    try:
        masters = (
            db.query(RejectionReasonMaster)
            .order_by(RejectionReasonMaster.id)
            .all()
        )
        result = []
        for m in masters:
            stages = [
                link.stage
                for link in sorted(m.stage_links, key=lambda x: (_STAGES.index(x.stage) if x.stage in _STAGES else 999, x.display_order))
            ]
            result.append({"reason_text": m.reason_text, "stages": stages})

        SEED_FILE.parent.mkdir(parents=True, exist_ok=True)
        SEED_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Exported {len(result)} rejection reasons to {SEED_FILE}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
