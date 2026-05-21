import { uploadPrescription, submitManualPrescription } from './api.js';
import { getCurrentUser } from './auth.js';
import { initAlerts } from './alerts.js';

const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const btnSelect = document.getElementById('btn-select-file');
const formManual = document.getElementById('form-manual');
const resultsSection = document.getElementById('results-section');
const alertContainer = document.getElementById('alert-container');

const confidenceBadge = document.getElementById('confidence-badge');
const prescriptionMeta = document.getElementById('prescription-meta');
const medsTbody = document.getElementById('meds-tbody');
const matchingSection = document.getElementById('matching-section');
const matchingPills = document.getElementById('matching-pills');
const ocrRaw = document.getElementById('ocr-raw');
const btnToggleOcr = document.getElementById('btn-toggle-ocr');
const ocrMeta = document.getElementById('ocr-meta');
const ocrModelChip = document.getElementById('ocr-model-chip');
const ocrBarFill = document.getElementById('ocr-bar-fill');
const ocrPct = document.getElementById('ocr-pct');
const ocrAttemptsChip = document.getElementById('ocr-attempts-chip');

function showAlert(message, type = 'danger') {
  if (alertContainer) alertContainer.innerHTML = `<div class="alert alert--${type}">${message}</div>`;
}

function clearAlert() {
  if (alertContainer) alertContainer.innerHTML = '';
}

btnToggleOcr?.addEventListener('click', () => {
  const hidden = ocrRaw?.style.display === 'none';
  if (ocrRaw) ocrRaw.style.display = hidden ? '' : 'none';
  if (btnToggleOcr) btnToggleOcr.textContent = hidden ? 'Masquer le texte OCR' : 'Voir le texte OCR brut';
});

function _val(v) {
  return v ?? '<span style="color:var(--color-text-muted);">—</span>';
}

function _tierClass(modelId) {
  if (!modelId) return '';
  if (modelId.endsWith(':free')) return 'tier-free';
  if (modelId.includes('haiku')) return 'tier-haiku';
  if (modelId.includes('sonnet') || modelId.includes('claude')) return 'tier-final';
  return '';
}

function _shortModelName(modelId) {
  if (!modelId || modelId === 'none') return 'Aucun modèle';
  const parts = modelId.replace(':free', '').split('/');
  return parts[parts.length - 1];
}

function showResults(data) {
  if (!resultsSection) return;
  resultsSection.style.display = '';

  const parsed = data.parsed_data ?? {};
  const meds = parsed.medications ?? data.medications ?? [];
  const doctor = parsed.doctor ?? {};
  const confidence = data.confidence ?? null;

  // OCR metadata strip
  const ocrConf = data.ocr_confidence ?? null;
  const ocrModel = data.ocr_model ?? null;
  const ocrAttempts = data.ocr_attempts ?? null;
  if (ocrMeta && ocrModel) {
    ocrMeta.style.display = '';
    if (ocrModelChip) {
      ocrModelChip.textContent = `🤖 ${_shortModelName(ocrModel)}`;
      ocrModelChip.className = `ocr-chip ${_tierClass(ocrModel)}`;
    }
    if (ocrConf !== null) {
      const pct = Math.round(ocrConf * 100);
      const color = pct >= 82 ? 'var(--color-secondary)' : pct >= 70 ? 'var(--color-warning)' : 'var(--color-danger)';
      if (ocrBarFill) { ocrBarFill.style.width = `${pct}%`; ocrBarFill.style.background = color; }
      if (ocrPct) ocrPct.textContent = `${pct}%`;
    }
    if (ocrAttempts !== null && ocrAttemptsChip) {
      ocrAttemptsChip.textContent = `${ocrAttempts} modèle${ocrAttempts > 1 ? 's' : ''} testé${ocrAttempts > 1 ? 's' : ''}`;
    }
  }

  // Confidence badge
  if (confidenceBadge) {
    if (confidence !== null) {
      const pct = Math.round(confidence * 100);
      confidenceBadge.textContent = `Confiance : ${pct}%`;
      confidenceBadge.className = `confidence-badge${pct < 70 ? ' low' : ''}`;
    } else {
      confidenceBadge.style.display = 'none';
    }
  }

  // Prescription meta (doctor, patient, date)
  if (prescriptionMeta) {
    const fields = [
      { label: 'Médecin', value: doctor.name },
      { label: 'Spécialité', value: doctor.speciality },
      { label: 'Ville', value: doctor.city },
      { label: 'Patient', value: parsed.patient_name },
      { label: 'Date', value: parsed.prescription_date },
    ].filter(f => f.value);

    prescriptionMeta.innerHTML = fields.length
      ? fields.map(f => `<div class="meta-item"><span>${f.label} : </span>${f.value}</div>`).join('')
      : '<div style="color:var(--color-text-muted);font-size:0.85rem;">Informations médecin/patient non détectées.</div>';
  }

  // Medications table
  if (medsTbody) {
    if (!meds.length) {
      medsTbody.innerHTML = '<tr><td colspan="5" style="color:var(--color-text-muted);">Aucun médicament extrait.</td></tr>';
    } else {
      medsTbody.innerHTML = meds.map(m => `
        <tr>
          <td><strong>${m.name ?? '—'}</strong></td>
          <td>${_val(m.dosage)}</td>
          <td>${_val(m.frequency)}</td>
          <td>${_val(m.duration)}</td>
          <td>${_val(m.quantity)}</td>
        </tr>
      `).join('');
    }
  }

  // Matching patients
  const matchingUsers = data.matching_users ?? [];
  if (matchingSection && matchingPills) {
    if (matchingUsers.length) {
      matchingSection.style.display = '';
      matchingPills.innerHTML = matchingUsers.map(u => {
        const sharedMeds = (u.medicaments ?? []).map(m => m.nom).join(', ');
        return `<span class="matching-pill">👤 ${u.pseudo} <small>${sharedMeds}</small></span>`;
      }).join('');
    } else {
      matchingSection.style.display = 'none';
    }
  }

  // OCR raw text
  if (ocrRaw) {
    ocrRaw.textContent = data.ocr_raw || '(aucun texte extrait)';
  }

  if (parsed.notes) {
    const notesEl = document.createElement('p');
    notesEl.style.cssText = 'margin-top:var(--spacing-sm);font-size:0.85rem;color:var(--color-text-muted);';
    notesEl.textContent = `Notes : ${parsed.notes}`;
    resultsSection.appendChild(notesEl);
  }
}

// ── Upload handlers ───────────────────────────────────────────────────────

btnSelect?.addEventListener('click', () => fileInput?.click());

uploadZone?.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
uploadZone?.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone?.addEventListener('drop', async (e) => {
  e.preventDefault();
  uploadZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) await handleFileUpload(file);
});

fileInput?.addEventListener('change', async () => {
  const file = fileInput.files[0];
  if (file) await handleFileUpload(file);
});

async function handleFileUpload(file) {
  clearAlert();
  showAlert('<span class="spinner"></span>Analyse en cours…', 'success');
  try {
    const user = await getCurrentUser();
    const result = await uploadPrescription(user?.id ?? 'anonymous', file);
    clearAlert();
    showResults(result);
  } catch (err) {
    showAlert(err.message);
  }
}

formManual?.addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    const lines = document.getElementById('manual-meds').value.trim().split('\n').filter(Boolean);
    const medications = lines.map(line => {
      const parts = line.trim().split(/\s+/);
      const name = parts[0] ?? '';
      const dosage = parts.slice(1).join(' ') || null;
      return { name, dosage };
    });
    const user = await getCurrentUser();
    const result = await submitManualPrescription(user?.id ?? 'anonymous', medications);
    showResults({ parsed_data: { medications: result.medications ?? [] }, ocr_raw: '', matching_users: [] });
  } catch (err) {
    showAlert(err.message);
  }
});

document.getElementById('btn-logout')?.addEventListener('click', (e) => {
  e.preventDefault();
  import('./auth.js').then(m => m.signOut());
});

initAlerts();
