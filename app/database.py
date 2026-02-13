import json
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Base, RejectionReasonMaster, StageReasonLink

DATABASE_URL = "sqlite:///./biochar.db"
SEED_FILE = Path(__file__).parent / "data" / "rejection_reasons_seed.json"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Normalize inconsistent variants to canonical text
_NORMALIZE_REASON = {
    "blur image": "Blurred Image",
    "blurred image": "Blurred Image",
    "geotag missing": "Missing Geotag Information",
    "geotag is missimg": "Missing Geotag Information",
    "geotag is missing": "Missing Geotag Information",
    "cut image": "Cut Image",
    "excess heat": "Excess Heat",
}

# Default rejection reasons per stage (raw, before normalization)
_DEFAULT_REJECTION_REASONS = {
    "moisture": [
        "Blurred Image", "Date Mismatch", "Duplicate Image Detected",
        "Incorrect Stage Image Uploaded", "Missing Geotag Information",
        "Moisture Meter Level Mismatch", "Timestamp Mismatch",
        "Date and Timestamp Mismatched", "Hold"
    ],
    "start": [
        "Blurred Image", "Date Mismatch", "Duplicate Image Detected",
        "Green Wood Detected in Kon Tiki", "Image Content Not Clearly Visible",
        "Incorrect Stage Image Uploaded", "Missing Geotag Information",
        "Multiple Kon Tiki Units in a Single Image", "Smoke Detected",
        "Timestamp Mismatch", "Visual Obstruction", "Kon Tiki Number Not Visible",
        "Miss Matched Kontiki Number", "Line error", "Cut Image",
        "Kontiki is filled too much"
    ],
    "mid": [
        "Blurred Image", "Clearly Visible Outside Kon Tiki", "Duplicate Image Detected",
        "Incorrect Stage Image Uploaded", "Kon Tiki Number Mismatch",
        "Kon Tiki Number Not Visible", "Missing Geotag Information",
        "Multiple Kon Tiki Units in a Single Image", "Smoke Detected",
        "Timestamp Mismatch", "Excess Heat", "Unburnt Biomass Clearly Visible",
        "Visual Obstruction", "Biomass is very low kontiki",
        "Hash content is more", "Error"
    ],
    "90": [
        "Missing Geotag Information", "Unburnt Biomass Clearly Visible",
        "Content Coverage Below 90%", "Duplicate Image Detected",
        "Smoke Detected", "Excess Heat or Content Visible Outside Kon Tiki",
        "Incorrect Stage Image Uploaded", "Kon Tiki Number Mismatch",
        "Kon Tiki Number Not Visible", "Multiple Kon Tiki Units in a Single Image",
        "Timestamp Mismatch", "Visual Obstruction", "Hash content is more",
        "Cut Image", "Blurred Image", "Content not visible"
    ],
    "end": [
        "Blurred Image", "Content Collected Directly from Ground",
        "Water Visible Inside Kon Tiki", "Unburnt Biomass Clearly Visible",
        "Visual Obstruction", "Date Mismatch", "Incorrect Stage Image Uploaded",
        "Kon Tiki Number Mismatch", "Kon Tiki Number Not Visible",
        "Multiple Kon Tiki Units in a Single Image", "Sand Visible Inside Kon Tiki",
        "Content is low", "Missing Geotag Information", "Cut Image",
        "Smoke Visible", "Kontiki is filled too much"
    ],
}


def _normalize_reason(raw: str) -> str:
    """Return canonical reason text for consistency."""
    key = raw.strip().lower()
    return _NORMALIZE_REASON.get(key, raw.strip() if raw else raw)


def init_db():
    Base.metadata.create_all(bind=engine)
    _drop_old_rejection_reasons_table()
    _seed_rejection_reasons()


def _drop_old_rejection_reasons_table():
    """Remove legacy single-table if it exists."""
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS rejection_reasons"))


def _seed_rejection_reasons():
    """Populate rejection_reason_master and stage_reason_link. Loads from app/data/rejection_reasons_seed.json if present, else uses built-in defaults."""
    db = SessionLocal()
    try:
        if db.query(RejectionReasonMaster).count() > 0:
            return

        # Try loading from seed file (committed to repo; fresh installs get these values)
        seed_list = _load_seed_from_file()
        if not seed_list:
            seed_list = _build_default_seed_list()

        # Track display_order per stage
        stage_order = {}
        for item in seed_list:
            reason_text = (item.get("reason_text") or "").strip()
            stages = item.get("stages") or []
            if not reason_text:
                continue
            master = RejectionReasonMaster(reason_text=reason_text)
            db.add(master)
            db.flush()
            for stage in stages:
                if stage in ("moisture", "start", "mid", "90", "end"):
                    order = stage_order.get(stage, 0)
                    db.add(StageReasonLink(master_id=master.id, stage=stage, display_order=order))
                    stage_order[stage] = order + 1
        db.commit()
    finally:
        db.close()


def _load_seed_from_file() -> list:
    """Load seed data from app/data/rejection_reasons_seed.json. Returns [] if file missing or invalid."""
    if not SEED_FILE.exists():
        return []
    try:
        data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _build_default_seed_list() -> list:
    """Build seed list from built-in _DEFAULT_REJECTION_REASONS (fallback when no seed file)."""
    reason_to_stages = {}
    for stage, reasons in _DEFAULT_REJECTION_REASONS.items():
        for order, raw in enumerate(reasons):
            canonical = _normalize_reason(raw)
            if canonical not in reason_to_stages:
                reason_to_stages[canonical] = {}
            reason_to_stages[canonical][stage] = order
    return [
        {"reason_text": rt, "stages": list(reason_to_stages[rt].keys())}
        for rt in sorted(reason_to_stages.keys())
    ]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
