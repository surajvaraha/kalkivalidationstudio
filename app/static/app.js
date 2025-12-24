
// State
let allRecords = [];
let currentBatchIndex = 0;
let currentStageIndex = 0; // 0: Moisture, 1: Start...

// Config from backend mapping
const STAGES = [
    { key: "wood_moisture", label: "Wood Moisture", imageCol: "Wood Moisture Image Link", statusCol: "Moisture is within limit", reasonCol: "Moisture Rejected remarks", commentCol: "Wood Moisture Comments", optionsType: "YES_NO" },
    { key: "process_start", label: "Process Start", imageCol: "Process Start Image Link", statusCol: "1.Process Start (Image)_Status", reasonCol: "1.Process Start (Image)_Status Remark", commentCol: "1.Process Start Comments", optionsType: "STATUS" },
    { key: "process_middle", label: "Process Middle", imageCol: "Process Middle Image Link", statusCol: "2.Process Middle (Image)_Status", reasonCol: "2.Process Middle (Image)_Status Remark", commentCol: "2.Process Middle Comments", optionsType: "STATUS" },
    { key: "90_percent", label: "90% Done", imageCol: "90% Done Image Link", statusCol: "3.90% (Image)_Status", reasonCol: "3.90% (Image)_Status Remark", commentCol: "3.90% Comments", optionsType: "STATUS" },
    { key: "process_end", label: "Process End", imageCol: "Process End Image Link", statusCol: "4.Process End (Image)_Status", reasonCol: "4.Process End (Image)_Status Remark", commentCol: "4.Process End Comments", optionsType: "STATUS" }
];

// Validation Options (Hardcoded for immediate responsiveness, could fetch from API)
const CONFIG = {
    STATUS_OPTIONS: ["Approved", "Rejected", "Under Query", "Link error"],
    YES_NO_OPTIONS: ["Yes", "No", "Under Query"],
    // Aggregate list for MVP. Ideal: Per-column lists.
    REJECTION_REASONS: [
        "Blurred Image", "Geotag Missing", "Unburnt Biomass Clearly Visible",
        "Kon Tiki Number Mismatch", "Visual Obstruction", "Other",
        "Date Mismatch", "Duplicate Image Detected" // Add more as per sheet
    ]
};

// DOM Elements
const mainWorkspace = document.getElementById('mainWorkspace');
const emptyState = document.getElementById('emptyState');
const statusSelect = document.getElementById('statusSelect');
const reasonSelect = document.getElementById('reasonSelect');
const commentsInput = document.getElementById('commentsInput');

// Init
document.getElementById('uploadBtn').addEventListener('click', () => document.getElementById('fileUpload').click());
document.getElementById('fileUpload').addEventListener('change', handleUpload);
document.getElementById('downloadBtn').addEventListener('click', () => window.location.href = '/api/download');

document.getElementById('prevBatch').addEventListener('click', () => loadBatch(currentBatchIndex - 1));
document.getElementById('nextBatch').addEventListener('click', () => loadBatch(currentBatchIndex + 1));

document.getElementById('prevStage').addEventListener('click', () => loadStage(currentStageIndex - 1));
document.getElementById('nextStage').addEventListener('click', () => loadStage(currentStageIndex + 1));

// Inputs Change Listeners (Auto-save)
statusSelect.addEventListener('change', () => saveCurrentStage());
reasonSelect.addEventListener('change', () => saveCurrentStage());
commentsInput.addEventListener('change', () => saveCurrentStage());

async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    // Reset UI
    allRecords = [];

    try {
        const res = await fetch('/api/upload', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.status === 'success') {
            allRecords = data.data;
            initWorkspace();
        } else {
            alert('Upload failed: ' + data.detail);
        }
    } catch (err) {
        console.error(err);
        alert('Error uploading file. Check console.');
    }
}

function initWorkspace() {
    emptyState.style.display = 'none';
    mainWorkspace.style.display = 'flex';
    document.getElementById('downloadBtn').disabled = false;
    currentBatchIndex = 0;
    currentStageIndex = 0;
    loadBatch(0);
}

function loadBatch(index) {
    if (index < 0 || index >= allRecords.length) return;
    currentBatchIndex = index;

    // Reset Stage
    currentStageIndex = 0;

    // Update Header
    document.getElementById('batchIndicator').textContent = `Batch ${index + 1} / ${allRecords.length}`;

    // Render Meta List
    renderMetaList(allRecords[index]);

    // Load First Stage
    loadStage(0);
}

function renderMetaList(record) {
    const list = document.getElementById('batchMetaList');
    // Key ID fields
    const keys = ["Batch_Kiln_ID", "Partner Name", "Facility Name", "production_start_date"];
    let html = '';
    keys.forEach(k => {
        let val = findValue(record, k) || '-';
        html += `<div><span>${k}</span>${val}</div>`;
    });
    list.innerHTML = html;
}

function loadStage(index) {
    if (index < 0 || index >= STAGES.length) return;
    currentStageIndex = index;

    const stage = STAGES[index];
    const record = allRecords[currentBatchIndex];

    // 1. Update Title
    document.getElementById('currentStageTitle').textContent = stage.label;

    // 2. Update Image
    const imgUrl = findValue(record, stage.imageCol);
    document.getElementById('mainImage').src = imgUrl || '';
    document.getElementById('mainImage').alt = imgUrl ? stage.label : "No Image Found";

    // 3. Update Inputs
    const statusVal = findValue(record, stage.statusCol);
    const reasonVal = findValue(record, stage.reasonCol);
    const commentVal = findValue(record, stage.commentCol);

    // Populate Selects
    populateSelect(statusSelect, stage.optionsType === "YES_NO" ? CONFIG.YES_NO_OPTIONS : CONFIG.STATUS_OPTIONS, statusVal);
    populateSelect(reasonSelect, CONFIG.REJECTION_REASONS, reasonVal); // Todo: filter reasons per stage if needed
    commentsInput.value = commentVal || '';

    // 4. Update Summary Table Highlight
    renderStatusTable(record);
}

function populateSelect(el, options, currentVal) {
    el.innerHTML = '<option value="">-- Select --</option>';
    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt;
        option.textContent = opt;
        if (opt === currentVal) option.selected = true;
        el.innerHTML += option.outerHTML;
    });
}

function renderStatusTable(record) {
    const tbody = document.querySelector('#statusTable tbody');
    tbody.innerHTML = '';

    STAGES.forEach((stage, idx) => {
        const val = findValue(record, stage.statusCol);
        const tr = document.createElement('tr');
        if (idx === currentStageIndex) tr.className = 'active-stage';

        // Status Class
        let statusClass = 'status-pending';
        if (val === 'Approved' || val === 'Yes') statusClass = 'status-approved';
        if (val === 'Rejected' || val === 'No' || val === 'Under Query') statusClass = 'status-rejected';

        tr.innerHTML = `
            <td>${stage.label}</td>
            <td class="${statusClass}">${val || 'Pending'}</td>
        `;
        tr.onclick = () => loadStage(idx);
        tbody.appendChild(tr);
    });
}

function saveCurrentStage() {
    const stage = STAGES[currentStageIndex];
    const record = allRecords[currentBatchIndex];

    // Update Local State
    const statusKey = Object.keys(record).find(k => k.includes(stage.statusCol));
    const reasonKey = Object.keys(record).find(k => k.includes(stage.reasonCol));
    const commentKey = Object.keys(record).find(k => k.includes(stage.commentCol));

    if (statusKey) record[statusKey] = statusSelect.value;
    if (reasonKey && reasonSelect.value) record[reasonKey] = reasonSelect.value;
    if (commentKey) record[commentKey] = commentsInput.value; // Write to comment col

    // Re-render table to show status change
    renderStatusTable(record);

    // Sync Backend
    const idKey = Object.keys(record).find(k => k.includes("Batch_Kiln_ID")) || Object.keys(record).find(k => k.includes("Batch Kiln ID"));
    const updates = {};
    if (statusKey) updates[statusKey] = statusSelect.value;
    if (reasonKey) updates[reasonKey] = reasonSelect.value;
    if (commentKey) updates[commentKey] = commentsInput.value;

    fetch('/api/update_batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            Batch_Kiln_ID: record[idKey],
            updates: updates
        })
    });
}

function findValue(record, keyFragment) {
    if (!record) return undefined;
    const key = Object.keys(record).find(k => k.includes(keyFragment));
    return key ? record[key] : undefined;
}
