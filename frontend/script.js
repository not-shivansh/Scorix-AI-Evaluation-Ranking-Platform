/* ══════════════════════════════════════════════════════════
   Scorix AI — Frontend Logic
   API integration, tab navigation, and dynamic UI rendering.
   ══════════════════════════════════════════════════════════ */

const API_BASE = window.location.origin;

// ─── Tab Navigation ──────────────────────────────────────
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Deactivate all
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

        // Activate selected
        btn.classList.add('active');
        const panelId = `panel-${btn.dataset.tab}`;
        document.getElementById(panelId).classList.add('active');
    });
});

// ─── Feedback Score Slider ───────────────────────────────
const fbScoreSlider = document.getElementById('fb-score');
const fbScoreDisplay = document.getElementById('fb-score-display');
if (fbScoreSlider) {
    fbScoreSlider.addEventListener('input', () => {
        fbScoreDisplay.textContent = parseFloat(fbScoreSlider.value).toFixed(1);
    });
}

// ─── File Upload ─────────────────────────────────────────
let selectedFile = null;
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const btnUpload = document.getElementById('btn-upload');

if (uploadZone) {
    uploadZone.addEventListener('click', () => fileInput.click());

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith('.csv')) {
            setFile(file);
        } else {
            showToast('Please upload a CSV file', 'error');
        }
    });
}

if (fileInput) {
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            setFile(fileInput.files[0]);
        }
    });
}

function setFile(file) {
    selectedFile = file;
    fileName.textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    fileInfo.classList.remove('hidden');
    uploadZone.classList.add('hidden');
    btnUpload.disabled = false;
}

function removeFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.classList.add('hidden');
    uploadZone.classList.remove('hidden');
    btnUpload.disabled = true;
}

// ─── API Handlers ────────────────────────────────────────

async function handleEvaluate() {
    const prompt = document.getElementById('eval-prompt').value.trim();
    const response = document.getElementById('eval-response').value.trim();

    if (!prompt || !response) {
        showToast('Please fill in both fields', 'error');
        return;
    }

    const btn = document.getElementById('btn-evaluate');
    setLoading(btn, true);

    try {
        const res = await fetch(`${API_BASE}/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, response }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Evaluation failed');
        }

        const data = await res.json();
        showEvalResult(data.score);
        showToast(`Score: ${data.score}/10`, 'success');
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
}

function showEvalResult(score) {
    const resultEl = document.getElementById('eval-result');
    const scoreValue = document.getElementById('score-value');
    const scoreCircle = document.getElementById('score-circle');

    resultEl.classList.remove('hidden');

    // Animate score number
    animateCounter(scoreValue, score);

    // Animate ring
    const circumference = 2 * Math.PI * 52; // r=52
    const offset = circumference - (score / 10) * circumference;
    scoreCircle.style.strokeDasharray = circumference;
    scoreCircle.style.strokeDashoffset = circumference;

    requestAnimationFrame(() => {
        scoreCircle.style.strokeDashoffset = offset;
    });
}

function animateCounter(el, target) {
    let current = 0;
    const step = target / 30;
    const interval = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(interval);
        }
        el.textContent = current.toFixed(1);
    }, 30);
}

async function handleRank() {
    const prompt = document.getElementById('rank-prompt').value.trim();
    const responseEls = document.querySelectorAll('.rank-response');
    const responses = [];

    responseEls.forEach(el => {
        const val = el.value.trim();
        if (val) responses.push(val);
    });

    if (!prompt) {
        showToast('Please enter a prompt', 'error');
        return;
    }

    if (responses.length < 2) {
        showToast('Please provide at least 2 responses', 'error');
        return;
    }

    const btn = document.getElementById('btn-rank');
    setLoading(btn, true);

    try {
        const res = await fetch(`${API_BASE}/rank`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, responses }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Ranking failed');
        }

        const data = await res.json();
        showRankResult(data.ranked_responses);
        showToast('Responses ranked!', 'success');
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
}

function showRankResult(ranked) {
    const resultEl = document.getElementById('rank-result');
    const listEl = document.getElementById('rank-list');

    resultEl.classList.remove('hidden');
    listEl.innerHTML = '';

    ranked.forEach((item, i) => {
        const badgeClass = i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : 'default';
        const div = document.createElement('div');
        div.className = 'rank-item';
        div.style.animationDelay = `${i * 0.1}s`;
        div.innerHTML = `
            <div class="rank-badge ${badgeClass}">#${item.rank}</div>
            <div class="rank-content">
                <p class="rank-text">${escapeHtml(item.response)}</p>
                <span class="rank-score">Score: ${item.score}/10</span>
            </div>
        `;
        listEl.appendChild(div);
    });
}

function addResponseField() {
    const container = document.getElementById('rank-responses-container');
    const count = container.querySelectorAll('.response-input').length + 1;
    const div = document.createElement('div');
    div.className = 'form-group response-input';
    div.innerHTML = `
        <label>Response ${count}</label>
        <textarea class="rank-response" rows="3" placeholder="Response ${count}..."></textarea>
    `;
    container.appendChild(div);
}

async function handleFeedback() {
    const prompt = document.getElementById('fb-prompt').value.trim();
    const response = document.getElementById('fb-response').value.trim();
    const score = parseFloat(document.getElementById('fb-score').value);

    if (!prompt || !response) {
        showToast('Please fill in prompt and response', 'error');
        return;
    }

    const btn = document.getElementById('btn-feedback');
    setLoading(btn, true);

    try {
        const res = await fetch(`${API_BASE}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, response, score }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Feedback submission failed');
        }

        showToast('Feedback submitted! Thank you.', 'success');

        // Clear form
        document.getElementById('fb-prompt').value = '';
        document.getElementById('fb-response').value = '';
        document.getElementById('fb-score').value = 5;
        fbScoreDisplay.textContent = '5.0';
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
}

async function handleUpload() {
    if (!selectedFile) {
        showToast('Please select a file first', 'error');
        return;
    }

    const btn = document.getElementById('btn-upload');
    setLoading(btn, true);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const res = await fetch(`${API_BASE}/upload-dataset`, {
            method: 'POST',
            body: formData,
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Upload failed');
        }

        const data = await res.json();
        showTrainResult(data);
        showToast('Model retrained successfully!', 'success');
        removeFile();
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
}

function showTrainResult(data) {
    const resultEl = document.getElementById('train-result');
    resultEl.classList.remove('hidden');

    document.getElementById('metric-mae').textContent = data.mae.toFixed(4);
    document.getElementById('metric-r2').textContent = data.r2.toFixed(4);
    document.getElementById('metric-samples').textContent = data.samples_used;
}

// ─── Utilities ───────────────────────────────────────────

function setLoading(btn, isLoading) {
    const text = btn.querySelector('.btn-text');
    const loader = btn.querySelector('.btn-loader');

    if (isLoading) {
        text.classList.add('hidden');
        loader.classList.remove('hidden');
        btn.disabled = true;
    } else {
        text.classList.remove('hidden');
        loader.classList.add('hidden');
        btn.disabled = false;
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
