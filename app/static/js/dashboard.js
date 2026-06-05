const API = '';
let timelineChart = null;
let severityChart = null;

function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = 'toast toast-' + type;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

async function api(method, path, payload) {
  const url = `${API}${path}`;
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (payload) opts.body = JSON.stringify(payload);
  const r = await fetch(url, opts);
  if (!r.ok) {
    const text = await r.text();
    throw new Error(`HTTP ${r.status}: ${text}`);
  }
  return r.json();
}

/* Health */
async function getHealth() {
  try {
    const d = await api('GET', '/health');
    const el = document.getElementById('health-badge');
    el.textContent = 'System Online';
    el.className = 'status-indicator status-online';
  } catch (e) {
    const el = document.getElementById('health-badge');
    el.textContent = 'API Unreachable';
    el.className = 'status-indicator status-offline';
  }
}

/* KPI Stats */
async function refreshStats() {
  try {
    const logs = await api('GET', '/logs/recent?limit=1');
    // No hay endpoint de count, usamos anomalías como proxy
    const anomalies = await api('GET', '/anomalies/recent?limit=100');
    const history = await api('GET', '/alerts/history?limit=100');

    const open = anomalies.filter(a => a.status === 'OPEN').length;
    const critical = anomalies.filter(a => a.severity === 'CRITICAL').length;
    const sent = history.filter(h => h.status === 'SENT').length;

    document.getElementById('stat-logs').textContent = anomalies.length > 0 ? '—' : '0';
    document.getElementById('stat-open').textContent = open;
    document.getElementById('stat-critical').textContent = critical;
    document.getElementById('stat-alerts').textContent = sent;
  } catch (e) {
    console.error('refreshStats', e);
  }
}

/* Ingest */
async function ingestLogs() {
  const raw = document.getElementById('log-input').value;
  const fmt = document.getElementById('log-format').value;
  const lines = raw.split('\n').filter(l => l.trim());
  if (!lines.length) {
    showToast('No log lines provided', 'error');
    return;
  }
  try {
    const d = await api('POST', '/logs/ingest', { raw_lines: lines, source_format: fmt });
    document.getElementById('ingest-feedback').textContent = `Ingested: ${d.ingested}, Failed: ${d.failed}`;
    showToast(`${d.ingested} logs ingested`);
    await loadAnomalies();
    await refreshStats();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

/* Detection */
async function runDetection() {
  try {
    const d = await api('POST', '/anomalies/detect');
    showToast(`${d.length} anomalies detected`);
    await loadAnomalies();
    await refreshStats();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

/* Anomalies Table */
function severityHtml(sev) {
  const map = {
    CRITICAL: 'severity-critical',
    HIGH: 'severity-high',
    MEDIUM: 'severity-medium',
    LOW: 'severity-low'
  };
  const cls = map[sev] || 'severity-medium';
  return `<span class="severity ${cls}"><span class="severity-dot"></span>${sev}</span>`;
}

function statusBadge(status) {
  if (status === 'OPEN') return '<span class="badge badge-danger">OPEN</span>';
  if (status === 'ACKNOWLEDGED') return '<span class="badge badge-secondary">ACK</span>';
  return '<span class="badge badge-success">RESOLVED</span>';
}

async function loadAnomalies() {
  try {
    const data = await api('GET', '/anomalies/recent?limit=50');
    const tbody = document.querySelector('#anomaly-table tbody');
    const empty = document.getElementById('anomaly-empty');
    const count = document.getElementById('anomaly-count');

    count.textContent = `${data.length} records`;

    if (!data.length) {
      tbody.innerHTML = '';
      empty.style.display = 'block';
      updateCharts([]);
      return;
    }

    empty.style.display = 'none';
    tbody.innerHTML = data.map(a => {
      const svc = (a.details.match(/Service '(.*?)'/) || [])[1] || '—';
      return `<tr>
        <td>#${a.id}</td>
        <td>${severityHtml(a.severity)}</td>
        <td>${svc}</td>
        <td style="max-width:320px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${a.details}</td>
        <td>${new Date(a.window_start).toLocaleTimeString()} – ${new Date(a.window_end).toLocaleTimeString()}</td>
        <td>${statusBadge(a.status)}</td>
        <td>${new Date(a.detected_at).toLocaleString()}</td>
      </tr>`;
    }).join('');

    updateCharts(data);
  } catch (e) {
    console.error('loadAnomalies', e);
  }
}

/* Charts */
function updateCharts(anomalies) {
  const tlCtx = document.getElementById('timelineChart');
  const sevCtx = document.getElementById('severityChart');
  if (!tlCtx || !sevCtx) return;

  const buckets = {};
  anomalies.forEach(a => {
    const m = new Date(a.detected_at).toISOString().slice(0, 16);
    buckets[m] = (buckets[m] || 0) + 1;
  });
  const labels = Object.keys(buckets).sort();
  const values = labels.map(l => buckets[l]);

  if (timelineChart) timelineChart.destroy();
  timelineChart = new Chart(tlCtx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Anomalies',
        data: values,
        borderColor: '#e9202f',
        backgroundColor: 'rgba(233,32,47,0.08)',
        fill: true,
        tension: 0.3,
        pointRadius: 4,
        pointBackgroundColor: '#e9202f',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#64748b', font: { size: 11 } } },
        y: { grid: { color: '#eaeaea' }, ticks: { color: '#64748b', font: { size: 11 }, stepSize: 1 } }
      }
    }
  });

  const sevCounts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
  anomalies.forEach(a => { if (sevCounts[a.severity] !== undefined) sevCounts[a.severity]++; });

  if (severityChart) severityChart.destroy();
  severityChart = new Chart(sevCtx, {
    type: 'bar',
    data: {
      labels: Object.keys(sevCounts),
      datasets: [{
        label: 'Count',
        data: Object.values(sevCounts),
        backgroundColor: ['#991b1b', '#d97706', '#2563eb', '#166534'],
        borderRadius: 6,
        barThickness: 32
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#64748b', font: { size: 11 } } },
        y: { grid: { color: '#eaeaea' }, ticks: { color: '#64748b', font: { size: 11 }, stepSize: 1 } }
      }
    }
  });
}

/* Alert Configs */
async function addConfig() {
  const url = document.getElementById('webhook-url').value.trim();
  if (!url) { showToast('Enter a webhook URL', 'error'); return; }
  try {
    await api('POST', '/alerts/configs', { webhook_url: url, event_types: ['ANOMALY'] });
    showToast('Webhook registered');
    await loadConfigs();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function loadConfigs() {
  try {
    const data = await api('GET', '/alerts/configs');
    const el = document.getElementById('config-list');
    if (!data.length) {
      el.innerHTML = 'No configs registered.';
      return;
    }
    el.innerHTML = data.map(c => `<div style="padding:8px 0;border-bottom:1px solid #eaeaea;">${c.webhook_url}</div>`).join('');
  } catch (e) {
    console.error('loadConfigs', e);
  }
}

async function triggerAlerts() {
  try {
    const d = await api('POST', '/alerts/trigger');
    document.getElementById('trigger-feedback').textContent = `${d.triggered} alerts triggered`;
    showToast(`${d.triggered} alerts triggered`);
    await loadHistory();
    await refreshStats();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function loadHistory() {
  try {
    const data = await api('GET', '/alerts/history?limit=20');
    const tbody = document.querySelector('#history-table tbody');
    const empty = document.getElementById('history-empty');

    if (!data.length) {
      tbody.innerHTML = '';
      empty.style.display = 'block';
      return;
    }
    empty.style.display = 'none';
    tbody.innerHTML = data.map(h => {
      const badge = h.status === 'SENT' ? '<span class="badge badge-success">SENT</span>' :
                    h.status === 'FAILED' ? '<span class="badge badge-danger">FAILED</span>' :
                    '<span class="badge badge-secondary">PENDING</span>';
      return `<tr>
        <td>${badge}</td>
        <td>${h.response_status ?? '—'}</td>
        <td>${h.sent_at ? new Date(h.sent_at).toLocaleString() : '—'}</td>
      </tr>`;
    }).join('');
  } catch (e) {
    console.error('loadHistory', e);
  }
}

/* Navigation */
document.querySelectorAll('.sidebar-nav a').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    document.querySelectorAll('.sidebar-nav a').forEach(l => l.classList.remove('active'));
    link.classList.add('active');
    const tab = link.dataset.tab;
    const targets = { overview: null, ingest: 'panel-ingest', anomalies: 'panel-anomalies', alerts: 'panel-alerts' };
    if (targets[tab]) {
      document.getElementById(targets[tab]).scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  });
});

/* Init */
async function init() {
  await getHealth();
  await loadAnomalies();
  await loadConfigs();
  await loadHistory();
  await refreshStats();
}

init();
setInterval(() => { getHealth(); loadAnomalies(); loadHistory(); refreshStats(); }, 15000);
