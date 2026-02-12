
# ─── Status / Reason Option Lists ──────────────────────────────────────────
YES_NO_QUERY = ["Yes", "No", "Under Query"]
STATUS_OPTIONS = ["Approved", "Rejected", "Under Query", "Link error"]

MOISTURE_REJECTION_REASONS = [
    "Blurred Image", "Date Mismatch", "Duplicate Image Detected",
    "Incorrect Stage Image Uploaded", "Missing Geotag Information",
    "Moisture Meter Level Mismatch", "Timestamp Mismatch",
    "Date and Timestamp Mismatched", "Hold"
]

GENERAL_REJECTION_REASONS = [
    "Blurred Image", "Clearly Visible Outside Kon Tiki", "Duplicate Image Detected",
    "Smoke Detected", "Incorrect Stage Image Uploaded", "Kon Tiki Number Mismatch",
    "Kon Tiki Number Not Visible", "Missing Geotag Information",
    "Multiple Kon Tiki Units in a Single Image", "Excess heat",
    "Timestamp Mismatch", "Unburnt Biomass Clearly Visible",
    "Visual Obstruction", "Biomass is very low kontiki",
    "Hash content is more", "Error", "Cut Image", "Content not visible"
]

# ─── Standard Stage Keys ───────────────────────────────────────────────────
# Kalki uses moisture_1..5 (5 separate meter images), Looker uses single 'moisture'
STAGES = [
    'moisture', 'moisture_1', 'moisture_2', 'moisture_3', 'moisture_4', 'moisture_5',
    'start', 'mid', '90', 'end',
]

def get_stages_for_task_type(task_type):
    """Return list of stages relevant to the task type."""
    from app.models import TaskType
    if task_type == TaskType.KALKI:
        return ['moisture_1', 'moisture_2', 'moisture_3', 'moisture_4', 'moisture_5',
                'start', 'mid', '90', 'end']
    elif task_type == TaskType.LOOKER:
        return ['moisture', 'start', 'mid', '90', 'end']
    return STAGES

# ─── Validation Schema ─────────────────────────────────────────────────────
# image_patterns: columns to search for the image URL (checked in order)
# status_col / reason_col / comment_col: OUTPUT column names written by exporter
VALIDATION_SCHEMA = [
    # Looker single moisture
    {
        "key": "moisture",
        "label": "Wood Moisture",
        "image_patterns": ["Wood Moisture Image Link", "Wood Moisture (Image)", "moisture_image"],
        "status_col": "Moisture Status",
        "status_options": YES_NO_QUERY,
        "reason_col": "Moisture Remark",
        "reason_options": MOISTURE_REJECTION_REASONS,
        "comment_col": "Moisture Comment",
    },
    # Kalki 5 moisture readings
    {
        "key": "moisture_1",
        "label": "Moisture 1",
        "image_patterns": ["Wood Moisture Image 1"],
        "status_col": "Moisture 1 Status",
        "status_options": YES_NO_QUERY,
        "reason_col": "Moisture 1 Remark",
        "reason_options": MOISTURE_REJECTION_REASONS,
        "comment_col": "Moisture 1 Comment",
    },
    {
        "key": "moisture_2",
        "label": "Moisture 2",
        "image_patterns": ["Wood Moisture Image 2"],
        "status_col": "Moisture 2 Status",
        "status_options": YES_NO_QUERY,
        "reason_col": "Moisture 2 Remark",
        "reason_options": MOISTURE_REJECTION_REASONS,
        "comment_col": "Moisture 2 Comment",
    },
    {
        "key": "moisture_3",
        "label": "Moisture 3",
        "image_patterns": ["Wood Moisture Image 3"],
        "status_col": "Moisture 3 Status",
        "status_options": YES_NO_QUERY,
        "reason_col": "Moisture 3 Remark",
        "reason_options": MOISTURE_REJECTION_REASONS,
        "comment_col": "Moisture 3 Comment",
    },
    {
        "key": "moisture_4",
        "label": "Moisture 4",
        "image_patterns": ["Wood Moisture Image 4"],
        "status_col": "Moisture 4 Status",
        "status_options": YES_NO_QUERY,
        "reason_col": "Moisture 4 Remark",
        "reason_options": MOISTURE_REJECTION_REASONS,
        "comment_col": "Moisture 4 Comment",
    },
    {
        "key": "moisture_5",
        "label": "Moisture 5",
        "image_patterns": ["Wood Moisture Image 5"],
        "status_col": "Moisture 5 Status",
        "status_options": YES_NO_QUERY,
        "reason_col": "Moisture 5 Remark",
        "reason_options": MOISTURE_REJECTION_REASONS,
        "comment_col": "Moisture 5 Comment",
    },
    # Process stages
    {
        "key": "start",
        "label": "Process Start",
        "image_patterns": ["Process Start (Image)", "Process Start Image Link",
                           "1.Process Start (Image)"],
        "status_col": "Process Start Status",
        "status_options": STATUS_OPTIONS,
        "reason_col": "Process Start Remark",
        "reason_options": GENERAL_REJECTION_REASONS,
        "comment_col": "Process Start Comment",
        "geotag_col": "Process Start Geotag",
        "serial_col": "Process Start Serial",
    },
    {
        "key": "mid",
        "label": "Process Middle",
        "image_patterns": ["Process Middle (Image)", "Process Middle Image Link",
                           "2.Process Middle (Image)"],
        "status_col": "Process Middle Status",
        "status_options": STATUS_OPTIONS,
        "reason_col": "Process Middle Remark",
        "reason_options": GENERAL_REJECTION_REASONS,
        "comment_col": "Process Middle Comment",
        "geotag_col": "Process Middle Geotag",
        "serial_col": "Process Middle Serial",
    },
    {
        "key": "90",
        "label": "90% Done",
        "image_patterns": ["90% Done (Image)", "90% Done Image Link",
                           "3.90% (Image)"],
        "status_col": "90% Done Status",
        "status_options": STATUS_OPTIONS,
        "reason_col": "90% Done Remark",
        "reason_options": GENERAL_REJECTION_REASONS,
        "comment_col": "90% Done Comment",
        "geotag_col": "90% Done Geotag",
        "serial_col": "90% Done Serial",
    },
    {
        "key": "end",
        "label": "Process End",
        "image_patterns": ["Process End (Image)", "Process End Image Link",
                           "4.Process End (Image)"],
        "status_col": "Process End Status",
        "status_options": STATUS_OPTIONS,
        "reason_col": "Process End Remark",
        "reason_options": GENERAL_REJECTION_REASONS,
        "comment_col": "Process End Comment",
        "geotag_col": "Process End Geotag",
        "serial_col": "Process End Serial",
    },
]
