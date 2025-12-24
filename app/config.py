
# Data Validation Lists (Extracted from "Validated Data" sheet)

# range J2:J527 (Moisture is within limit?), etc.
YES_NO_QUERY = ["Yes", "No", "Under Query"]

# range N2:N527 (Image Status)
STATUS_OPTIONS = ["Approved", "Rejected", "Under Query", "Link error"]

# Range K2:K527 (Moisture Rejected remarks)
MOISTURE_REJECTION_REASONS = [
    "Blurred Image", "Date Mismatch", "Duplicate Image Detected", 
    "Incorrect Stage Image Uploaded", "Missing Geotag Information", 
    "Moisture Meter Level Mismatch", "Timestamp Mismatch", 
    "Date and Timestamp Mismatched", "Hold"
]

# Range Z2:Z527 (Process Start? Varies by column usually, but looks like a general list for Kon Tiki)
# This list seems to cover many issues.
GENERAL_REJECTION_REASONS = [
    "Blurred Image", "Clearly Visible Outside Kon Tiki", "Duplicate Image Detected", 
    "Smoke Detected", "Incorrect Stage Image Uploaded", "Kon Tiki Number Mismatch", 
    "Kon Tiki Number Not Visible", "Missing Geotag Information", 
    "Multiple Kon Tiki Units in a Single Image", "Excess heat", 
    "Timestamp Mismatch", "Unburnt Biomass Clearly Visible", 
    "Visual Obstruction", "Biomass is very low kontiki", 
    "Hash content is more", "Error", "Cut Image", "Content not visible"
]

# Range AL2 (Process Middle/End variants?) - "Content Collected Directly from Ground"
# It seems there are slightly different lists for different stages. 
# For MVP, we can try to map them precisely or use a Union if unsure.
# Let's try to map generic "Reason" lists to the stages based on user intent.

# Standard Stage Keys used throughout the system
STAGES = ['moisture', 'start', 'mid', '90', 'end']

# Column Mapping for Looker & Kalki compatibility
# This dictates: 1) What columns are available 2) What choices they have
VALIDATION_SCHEMA = [
    {
        "key": "moisture",
        "label": "Wood Moisture",
        "image_patterns": ["Wood Moisture Image Link", "Wood Moisture (Image)", "moisture_image"],
        "status_col": "Moisture is within limit",
        "status_options": YES_NO_QUERY,
        "reason_col": "Moisture Rejected remarks",
        "reason_options": MOISTURE_REJECTION_REASONS,
        "comment_col": "Wood Moisture Comments"
    },
    {
        "key": "start",
        "label": "Process Start",
        "image_patterns": ["Process Start Image Link", "1.Process Start (Image)", "start_image", "Process Start (Image)"],
        "status_col": "1.Process Start (Image)_Status",
        "status_options": STATUS_OPTIONS,
        "reason_col": "1.Process Start (Image)_Status Remark",
        "reason_options": GENERAL_REJECTION_REASONS,
        "comment_col": "1.Process Start Comments"
    },
    {
        "key": "mid",
        "label": "Process Middle",
        "image_patterns": ["Process Middle Image Link", "2.Process Middle (Image)", "mid_image", "Process Middle (Image)"],
        "status_col": "2.Process Middle (Image)_Status",
        "status_options": STATUS_OPTIONS,
        "reason_col": "2.Process Middle (Image)_Status Remark",
        "reason_options": GENERAL_REJECTION_REASONS,
        "comment_col": "2.Process Middle Comments"
    },
    {
        "key": "90",
        "label": "90% Done",
        "image_patterns": ["90% Done Image Link", "3.90% (Image)", "90_image", "90% Done (Image)"],
        "status_col": "3.90% (Image)_Status",
        "status_options": STATUS_OPTIONS,
        "reason_col": "3.90% (Image)_Status Remark",
        "reason_options": GENERAL_REJECTION_REASONS,
        "comment_col": "3.90% Comments"
    },
    {
        "key": "end",
        "label": "Process End",
        "image_patterns": ["Process End Image Link", "4.Process End (Image)", "end_image", "Process End (Image)"],
        "status_col": "4.Process End (Image)_Status",
        "status_options": STATUS_OPTIONS,
        "reason_col": "4.Process End (Image)_Status Remark",
        "reason_options": GENERAL_REJECTION_REASONS,
        "comment_col": "4.Process End Comments"
    }
]
