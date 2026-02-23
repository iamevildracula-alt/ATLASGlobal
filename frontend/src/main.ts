import './index.css'
import { DigitalTwinMap, ViewDimension } from './components/DigitalTwinMap';
import { HistoryChart } from './components/HistoryChart';
import { PolicyEditor } from './components/PolicyEditor';
import { NuclearControl } from './components/NuclearControl';

const API_BASE = 'http://localhost:8000/api';

// State
let networkMap: DigitalTwinMap | null = null;
let historyChartDemand: HistoryChart | null = null;
let historyChartCarbon: HistoryChart | null = null;
let policyEditor: PolicyEditor | null = null;
let nuclearControl: NuclearControl | null = null;
let nuclearTelemetryInterval: any = null;
let telemetryWS: WebSocket | null = null;

async function fetchMetrics() {
    try {
        const response = await fetch(`${API_BASE}/ingestion/metrics`);
        const data = await response.json();
        const demandEl = document.getElementById('val-demand');
        if (demandEl) demandEl.innerText = `${data.current_demand} MW`;

        const availEl = document.getElementById('val-availability');
        if (availEl) availEl.innerText = `${data.availability * 100}%`;

        const carbonEl = document.getElementById('val-carbon');
        if (carbonEl) carbonEl.innerText = `42.5 t`; // Mock
    } catch (e) {
        console.error('Failed to fetch metrics', e);
    }
}

function initTelemetryWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//localhost:8000/api/telemetry/live`;

    console.log(`Connecting to telemetry stream: ${wsUrl}`);
    telemetryWS = new WebSocket(wsUrl);

    telemetryWS.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'telemetry') {
                updateUIWithTelemetry(data);
            }
        } catch (e) {
            console.error('Failed to parse telemetry message', e);
        }
    };

    telemetryWS.onclose = () => {
        console.warn('Telemetry WebSocket closed. Retrying in 5s...');
        setTimeout(initTelemetryWebSocket, 5000);
    };

    telemetryWS.onerror = (err) => {
        console.error('Telemetry WebSocket error:', err);
    };
}

function updateUIWithTelemetry(data: any) {
    if (data.data_type === 'demand_mw') {
        const el = document.getElementById('val-demand');
        if (el) el.innerText = `${data.value.toFixed(1)} MW`;
    } else if (data.data_type === 'status') {
        fetchMetrics(); // Force full refresh on status change
    }

    // Update map if available
    if (networkMap) {
        // networkMap.updateTelemetry(data); // Future enhancement
    }
}

async function fetchScenarios() {
    try {
        const response = await fetch(`${API_BASE}/scenarios/`);
        const scenarios = await response.json();
        const list = document.getElementById('scenario-list');
        if (!list) return;

        list.innerHTML = '';

        scenarios.forEach((s: any) => {
            const btn = document.createElement('button');
            btn.className = 'scenario-btn';
            btn.innerHTML = `
                <div style="font-weight: 600">${s.type.replace('_', ' ').toUpperCase()}</div>
                <div style="font-size: 0.8rem; color: var(--text-dim)">${s.description}</div>
            `;
            btn.onclick = () => runDecision(s, btn);
            list.appendChild(btn);
        });
    } catch (e) {
        console.error('Failed to fetch scenarios', e);
    }
}

async function runDecision(scenario: any, btn: HTMLElement) {
    // UI update
    document.querySelectorAll('.scenario-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const titleEl = document.getElementById('rec-title');
    if (titleEl) titleEl.innerText = 'Analyzing Infrastructure Data...';

    try {
        const response = await fetch(`${API_BASE}/decisions/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(scenario)
        });
        const decision = await response.json();

        // Update Recommendation Header
        if (titleEl) titleEl.innerText = decision.summary;

        const actionEl = document.getElementById('rec-action');
        if (actionEl) actionEl.innerText = decision.recommended_action;

        // Primary Factor
        const factorEl = document.getElementById('rec-primary-factor');
        if (factorEl) {
            factorEl.innerText = `Driver: ${decision.primary_factor}`;
            factorEl.className = 'badge badge-warning';
        }

        // Trade-offs
        const tradeOffsEl = document.getElementById('rec-trade-offs');
        if (tradeOffsEl) {
            tradeOffsEl.innerHTML = '';

            const pFactor = decision.primary_factor;
            let fakeTradeOffs: any[] = [];
            if (pFactor.includes('Reliability')) {
                fakeTradeOffs.push({ aspect: 'Reliability', impact: 'Low', desc: 'Secure' });
                fakeTradeOffs.push({ aspect: 'Cost', impact: 'High', desc: 'Premium' });
            } else if (pFactor.includes('Cost')) {
                fakeTradeOffs.push({ aspect: 'Cost', impact: 'Low', desc: 'Optimized' });
                fakeTradeOffs.push({ aspect: 'Reliability', impact: 'Medium', desc: 'Standard' });
            } else {
                fakeTradeOffs.push({ aspect: 'Carbon', impact: 'Low', desc: 'Green' });
                fakeTradeOffs.push({ aspect: 'Cost', impact: 'Medium', desc: 'Standard' });
            }

            tradeOffsEl.innerHTML = fakeTradeOffs.map(t =>
                `<span class="trade-off-tag impact-${t.impact}">${t.aspect}: ${t.impact}</span>`
            ).join('');
        }

        // Risks
        const risksList = document.getElementById('rec-risks');
        if (risksList) {
            risksList.innerHTML = decision.risks.map((r: string) => `<li>${r}</li>`).join('');
        }

        // Alternatives
        const altList = document.getElementById('rec-alternatives');
        if (altList) {
            altList.innerHTML = decision.alternatives.map((alt: any) => `
                <div class="alternative-item">
                    <div style="font-weight: 600; font-size: 0.9rem">${alt.option_name}</div>
                    <div style="display: flex; gap: 1rem; font-size: 0.8rem; color: var(--text-dim); margin-top: 0.25rem;">
                       <span>Cost: $${Math.round(alt.cost_impact / 1000)}k</span>
                       <span>Rel: ${(alt.reliability_score * 100).toFixed(1)}%</span>
                       <span>CO2: ${Math.round(alt.carbon_impact)}t</span>
                    </div>
                </div>
            `).join('');
        }

        const confBadge = document.getElementById('conf-level');
        if (confBadge) {
            confBadge.innerText = `Confidence: ${Math.round(decision.confidence_level * 100)}%`;
            confBadge.className = `badge ${decision.confidence_level > 0.8 ? 'badge-success' : 'badge-warning'}`;
        }

        // --- Explainability Bridge: AI Rationale ---
        const rationaleEl = document.getElementById('rec-rationale');
        const rationaleContainer = document.getElementById('rec-rationale-container');
        if (rationaleEl && rationaleContainer) {
            if (decision.rationale) {
                rationaleEl.innerText = decision.rationale;
                rationaleContainer.style.display = 'block';
            } else {
                rationaleContainer.style.display = 'none';
            }
        }

    } catch (e) {
        console.error('Failed to run decision', e);
        if (titleEl) titleEl.innerText = 'Analysis Failed';
    }
}

// Navigation
function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            const viewId = item.getAttribute('data-view');
            if (viewId) switchView(viewId, item as HTMLElement);
        });
    });
}

function switchView(viewId: string, navItem: HTMLElement) {
    // Nav Active State
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    navItem.classList.add('active');

    // View Visibility
    document.querySelectorAll('.view-section').forEach(el => {
        (el as HTMLElement).style.display = 'none';
    });

    const target = document.getElementById(viewId);
    if (target) {
        target.style.display = viewId === 'view-map' ? 'flex' : 'block';
    }

    const mainContent = document.querySelector('.main-content');
    if (viewId === 'view-map') {
        mainContent?.classList.add('no-padding');
        initFullMapLogic();
    } else {
        mainContent?.classList.remove('no-padding');
    }


    // Init or refresh components if needed
    if (viewId === 'view-map') {
        if (!networkMap) {
            initNetworkMap();
        } else {
            networkMap.refresh();
        }
    }
    if (viewId === 'view-history') {
        if (!historyChartDemand) {
            initHistory();
        } else {
            historyChartDemand.refresh();
            historyChartCarbon?.refresh();
        }
    }
    if (viewId === 'view-policy') {
        if (!policyEditor) {
            policyEditor = new PolicyEditor('policy-editor-container');
        } else {
            policyEditor.fetchPolicy();
        }
    }
    if (viewId === 'view-nuclear') {
        if (!nuclearControl) {
            nuclearControl = new NuclearControl('reactor-core-gauge');
        }
        startNuclearTelemetry();
    } else {
        stopNuclearTelemetry();
    }
}

function startNuclearTelemetry() {
    if (nuclearTelemetryInterval) return;

    // Simulate reactor dynamics for the demo
    let temp = 285.0;

    nuclearTelemetryInterval = setInterval(() => {
        if (!nuclearControl) return;

        // Add some random noise and slight drift
        temp += (Math.random() - 0.45) * 2;
        if (temp < 280) temp = 280;

        const pressure = 15.5 + (temp - 285) * 0.01;
        const margin = Math.max(0, (700 - temp) / (700 - 285));

        nuclearControl.updateState(temp, pressure, margin, temp > 690);
    }, 1000);
}

function stopNuclearTelemetry() {
    if (nuclearTelemetryInterval) {
        clearInterval(nuclearTelemetryInterval);
        nuclearTelemetryInterval = null;
    }
}

async function initNetworkMap() {
    try {
        networkMap = new DigitalTwinMap('network-map-container');
        const response = await fetch(`${API_BASE}/infrastructure/topology`);
        const data = await response.json();
        networkMap.setData(data.nodes, data.links);

        // Check for faults
        const hasFault = data.links.some((l: any) => l.status === 'failed');
        if (hasFault) {
            const alert = document.getElementById('fault-alert');
            if (alert) alert.style.display = 'block';
        }

        // Setup dimension toggles
        document.querySelectorAll('.dim-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const dim = (e.target as HTMLElement).getAttribute('data-dim') as ViewDimension;
                if (networkMap && dim) {
                    networkMap.setDimension(dim);

                    // Update UI state
                    document.querySelectorAll('.dim-btn').forEach(b => {
                        (b as HTMLElement).style.background = '#333';
                        (b as HTMLElement).style.borderColor = '#444';
                    });
                    (e.target as HTMLElement).style.background = 'linear-gradient(135deg, var(--primary) 0%, #4facfe 100%)';
                    (e.target as HTMLElement).style.webkitBackgroundClip = 'text';
                    (e.target as HTMLElement).style.backgroundClip = 'text';
                    (e.target as HTMLElement).style.webkitTextFillColor = 'transparent';
                    (e.target as HTMLElement).style.borderColor = 'var(--primary)';
                }
            });
        });

    } catch (e) {
        console.error("Failed to load map data", e);
    }
}

async function initHistory() {
    try {
        historyChartDemand = new HistoryChart('history-chart-demand', 'System Demand (MW)', '#4dabf7');
        historyChartCarbon = new HistoryChart('history-chart-carbon', 'Carbon Intensity (t/MWh)', '#51cf66');

        const res = await fetch(`${API_BASE}/history/series`);
        const data = await res.json();

        historyChartDemand.setData(data.data.map((d: any) => ({ timestamp: d.timestamp, value: d.demand_mw })));
        historyChartCarbon.setData(data.data.map((d: any) => ({ timestamp: d.timestamp, value: d.carbon_intensity })));
    } catch (e) {
        console.error("Failed to load history data", e);
    }
}

// Initial Load
window.addEventListener('load', () => {
    fetchMetrics();
    fetchScenarios();
    initNavigation();
    initTelemetryWebSocket();
});

function initFullMapLogic() {
    const btn = document.getElementById('full-map-btn');
    const viewMap = document.getElementById('view-map');
    const sidebar = document.querySelector('.sidebar');

    if (btn && viewMap && sidebar) {
        btn.onclick = () => {
            const isFull = viewMap.classList.toggle('fullscreen-mode');
            (sidebar as HTMLElement).style.display = isFull ? 'none' : 'flex';

            if (isFull) {
                btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14h6v6M20 10h-6V4M14 10l7-7M10 14l-7 7"/></svg> Exit Full Screen`;
                btn.style.background = 'var(--danger)';
            } else {
                btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg> Full Screen`;
                btn.style.background = '#333';
            }

            if (networkMap) networkMap.refresh();
        };
    }
}
