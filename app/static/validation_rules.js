// Rejection Reasons defined in SOP (Kalki only)
const REJECTION_REASONS = {
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
        "Sand Visible Inside Kon Tiki", "Content is low", "Geotag is Missimg [sic]", "Cut image", 
        "Smoke Visible", "Kontiki is filled too much"
    ]
};

// Global function to be called by validation.html
window.updateRejectionReasons = function(taskType, stage) {
    const select = document.getElementById('reasonSelect');
    const currentValue = select.value;
    
    select.innerHTML = '<option value="">Select Reason...</option>';
    
    // Normalize stage (moisture_1..5 use same reasons as moisture)
    const stageKey = (stage && typeof stage === 'string' && stage.startsWith('moisture')) ? 'moisture' : stage;
    const reasons = REJECTION_REASONS[stageKey] || [];
    
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
