function switchTab(tab, el) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.remove('hidden');
    el.classList.add('active');
    if (tab === 'experiments') loadExps();
    if (tab === 'registry') loadRegistry();
}

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
let columns = [], selectedFeatures = new Set();

dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', (e) => { e.preventDefault(); });
dropZone.addEventListener('drop', (e) => { e.preventDefault(); if (e.dataTransfer.files[0]) uploadFile(e.dataTransfer.files[0]); });
fileInput.addEventListener('change', (e) => { if (e.target.files[0]) uploadFile(e.target.files[0]); });

async function uploadFile(file) {
    dropZone.innerHTML = '<p>Uploading...</p>';
    const fd = new FormData(); fd.append('file', file);
    try {
        const res = await fetch('/api/upload', { method: 'POST', body: fd });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        columns = data.columns;
        dropZone.innerHTML = `<p>✅ ${data.filename} (${data.rows} rows)</p>`;

        const info = document.getElementById('datasetInfo');
        info.classList.remove('hidden');
        info.innerHTML = Object.entries(data.stats).map(([col, s]) =>
            `<div class="ds-stat"><strong>${col}</strong>: ${s.dtype} · ${s.unique} unique · ${s.missing} missing</div>`
        ).join('');

        const targetCol = document.getElementById('targetCol');
        targetCol.innerHTML = columns.map(c => `<option value="${c}">${c}</option>`).join('');

        const checks = document.getElementById('featureChecks');
        selectedFeatures = new Set(columns.filter(c => c !== columns[columns.length - 1]));
        renderFeatureChecks();

        document.getElementById('configCard').classList.remove('hidden');
    } catch (err) { dropZone.innerHTML = `<p style="color:#f87171">${err.message}</p>`; }
}

function renderFeatureChecks() {
    const checks = document.getElementById('featureChecks');
    checks.innerHTML = columns.map(c => `<div class="check-item ${selectedFeatures.has(c) ? 'selected' : ''}" onclick="toggleFeature('${c}', this)">${c}</div>`).join('');
}
function toggleFeature(col, el) { selectedFeatures.has(col) ? selectedFeatures.delete(col) : selectedFeatures.add(col); el.classList.toggle('selected'); }

async function runExp() {
    const btn = document.getElementById('runBtn');
    btn.disabled = true; btn.textContent = '⏳ Training...';

    const fd = new FormData();
    fd.append('target', document.getElementById('targetCol').value);
    fd.append('features', [...selectedFeatures].join(','));
    fd.append('model_type', document.getElementById('modelType').value);

    try {
        const res = await fetch('/api/experiment', { method: 'POST', body: fd });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        renderResult(data);
    } catch (err) { alert('Error: ' + err.message); }

    btn.disabled = false; btn.textContent = '▶ Run Experiment';
}

function renderResult(data) {
    const card = document.getElementById('resultCard');
    card.classList.remove('hidden');

    const m = data.metrics;
    document.getElementById('metricCards').innerHTML = `
        <div class="metric-card"><div class="m-val">${m.accuracy}%</div><div class="m-label">Accuracy</div></div>
        <div class="metric-card"><div class="m-val">${m.precision}%</div><div class="m-label">Precision</div></div>
        <div class="metric-card"><div class="m-val">${m.recall}%</div><div class="m-label">Recall</div></div>
        <div class="metric-card"><div class="m-val">${m.f1}%</div><div class="m-label">F1 Score</div></div>
    `;

    const imps = data.feature_importances;
    if (Object.keys(imps).length > 0) {
        const maxImp = Math.max(...Object.values(imps));
        document.getElementById('importances').innerHTML = '<p style="font-size:0.8rem;color:#888;margin-bottom:8px">Feature Importances</p>' +
            Object.entries(imps).map(([name, val]) =>
                `<div class="imp-bar"><span class="imp-name">${name}</span><div class="imp-fill" style="width:${val/maxImp*200}px"></div><span class="imp-val">${val}%</span></div>`
            ).join('');
    }

    card.scrollIntoView({ behavior: 'smooth' });
}

async function loadExps() {
    const res = await fetch('/api/experiments');
    const data = await res.json();
    document.getElementById('expList').innerHTML = data.experiments.length === 0
        ? '<p style="color:#555;font-size:0.82rem">No experiments yet</p>'
        : data.experiments.map(e => `
            <div class="exp-row">
                <div><div class="exp-info">${e.model_type} · ${e.dataset.features.length} features</div><div class="exp-meta">${e.timestamp} · ${e.elapsed_seconds}s</div></div>
                <div style="text-align:right"><div class="exp-acc">${e.metrics.accuracy}%</div><button class="btn-sm" onclick="regModel('${e.id}','${e.model_type}')">Register</button></div>
            </div>
        `).join('');
}

async function regModel(expId, name) {
    await fetch('/api/register', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({experiment_id: expId, name}) });
    switchTab('registry', document.querySelectorAll('.tab')[2]);
}

async function loadRegistry() {
    const res = await fetch('/api/registry');
    const data = await res.json();
    document.getElementById('regList').innerHTML = data.models.length === 0
        ? '<p style="color:#555;font-size:0.82rem">No models registered</p>'
        : data.models.map(m => `
            <div class="reg-row">
                <div><span class="reg-name">${m.name}</span> <span class="reg-ver">v${m.version}</span></div>
                <div style="display:flex;gap:6px;align-items:center">
                    <span class="stage-badge st-${m.stage}">${m.stage}</span>
                    <select onchange="setStage('${m.id}',this.value)" style="padding:3px 6px;background:#0a0a12;border:1px solid #2a2b38;border-radius:4px;color:#ccc;font-size:0.72rem">
                        ${['development','staging','production','archived'].map(s => `<option value="${s}" ${s===m.stage?'selected':''}>${s}</option>`).join('')}
                    </select>
                </div>
            </div>
        `).join('');
}

async function setStage(id, stage) {
    await fetch('/api/stage', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({model_id: id, stage}) });
    loadRegistry();
}
