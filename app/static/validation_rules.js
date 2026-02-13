// Rejection Reasons – fetched from the database via API
// Fallback hardcoded reasons used only if the API call fails
const REJECTION_REASONS_FALLBACK = {
    moisture: [
        "Blurred Image", "Date Mismatch", "Duplicate Image Detected", "Incorrect Stage Image Uploaded",
        "Missing Geotag Information", "Moisture Meter Level Mismatch", "Timestamp Mismatch", 
        "Date and Timestamp Mismatched", "Hold"
    ],
    start: [
        "Blurred Image", "Date Mismatch", "Duplicate Image Detected", "Green Wood Detected in Kon Tiki",
        "Image Content Not Clearly Visible", "Incorrect Stage Image Uploaded", "Missing Geotag Information",
        "Multiple Kon Tiki Units in a Single Image", "Smoke Detected", "Timestamp Mismatch", "Visual Obstruction",
        "Kon Tiki Number Not Visible", "Miss Matched Kontiki Number", "Line error", "Cut image", 
        "Kontiki is filled too much"
    ],
    mid: [
        "Blurred Image", "Clearly Visible Outside Kon Tiki", "Duplicate Image Detected", "Incorrect Stage Image Uploaded",
        "Kon Tiki Number Mismatch", "Kon Tiki Number Not Visible", "Missing Geotag Information", 
        "Multiple Kon Tiki Units in a Single Image", "Smoke Detected", "Timestamp Mismatch", "Excess heat",
        "Unburnt Biomass Clearly Visible", "Visual Obstruction", "Biomass is very low kontiki", 
        "Hash content is more", "Error"
    ],
    '90': [
        "Geotag Missing", "Unburnt Biomass Clearly Visible", "Content Coverage Below 90%", "Duplicate Image Detected",
        "Smoke Detected", "Excess Heat or Content Visible Outside Kon Tiki", "Incorrect Stage Image Uploaded",
        "Kon Tiki Number Mismatch", "Kon Tiki Number Not Visible", "Multiple Kon Tiki Units in a Single Image",
        "Timestamp Mismatch", "Visual Obstruction", "Hash content is more", "Cut image", "Blur image", 
        "Content not visible"
    ],
    end: [
        "Blurred Image", "Content Collected Directly from Ground", "Water Visible Inside Kon Tiki", 
        "Unburnt Biomass Clearly Visible", "Visual Obstruction", "Date Mismatch", "Incorrect Stage Image Uploaded",
        "Kon Tiki Number Mismatch", "Kon Tiki Number Not Visible", "Multiple Kon Tiki Units in a Single Image",
        "Sand Visible Inside Kon Tiki", "Content is low", "Geotag is Missimg", "Cut image", 
        "Smoke Visible", "Kontiki is filled too much"
    ]
};

// Live data from the API (populated on first use / page load)
let REJECTION_REASONS = null;
let _rrFetchPromise = null;

/**
 * Fetch rejection reasons from the database.
 * Returns the grouped object { stage: [reason_string, ...] }.
 * Caches after first successful call; use refreshRejectionReasons() to reload.
 */
async function fetchRejectionReasons() {
    if (REJECTION_REASONS) return REJECTION_REASONS;
    if (_rrFetchPromise) return _rrFetchPromise;

    _rrFetchPromise = fetch('/api/rejection-reasons')
        .then(res => {
            if (!res.ok) throw new Error('Failed to fetch rejection reasons');
            return res.json();
        })
        .then(data => {
            // API returns { stage: [{id, reason, display_order}, ...] }
            // Convert to simple { stage: [reason_string, ...] }
            const simple = {};
            for (const [stage, items] of Object.entries(data)) {
                simple[stage] = items.map(i => i.reason);
            }
            REJECTION_REASONS = simple;
            _rrFetchPromise = null;
            return REJECTION_REASONS;
        })
        .catch(err => {
            console.warn('Could not load rejection reasons from API, using fallback:', err);
            REJECTION_REASONS = REJECTION_REASONS_FALLBACK;
            _rrFetchPromise = null;
            return REJECTION_REASONS;
        });

    return _rrFetchPromise;
}

/**
 * Force a fresh reload from the database on next use.
 */
function refreshRejectionReasons() {
    REJECTION_REASONS = null;
    _rrFetchPromise = null;
}

// Pre-fetch on script load so data is ready when the user needs it
fetchRejectionReasons();

// Global function to be called by validation.html
window.updateRejectionReasons = async function(taskType, stage) {
    const select = document.getElementById('reasonSelect');
    const currentValue = select.value;

    select.innerHTML = '<option value="">Select Reason...</option>';

    // Ensure we have the data
    const allReasons = await fetchRejectionReasons();

    // Normalize stage (moisture_1..5 use same reasons as moisture)
    const stageKey = (stage && typeof stage === 'string' && stage.startsWith('moisture')) ? 'moisture' : stage;
    const reasons = allReasons[stageKey] || [];

    reasons.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r;
        opt.innerText = r;
        select.appendChild(opt);
    });

    // Restore value if it still exists in the new list
    if (currentValue) {
        select.value = currentValue;
    }
}
