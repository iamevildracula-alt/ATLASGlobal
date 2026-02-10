import './index.css'
import { NetworkMap } from './components/NetworkMap';
import { HistoryChart } from './components/HistoryChart';
import { PolicyEditor } from './components/PolicyEditor';

const API_BASE = 'http://localhost:8000/api';

// State
let networkMap: NetworkMap | null = null;
let historyChartDemand: HistoryChart | null = null;
let historyChartCarbon: HistoryChart | null = null;
let policyEditor: PolicyEditor | null = null;
let currentView = 'view-overview';

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
            body: JSON.stringify({ scenario: scenario })
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

    currentView = viewId;

    // Init components if needed
    if (viewId === 'view-map' && !networkMap) {
        initNetworkMap();
    }
    if (viewId === 'view-history' && !historyChartDemand) {
        initHistory();
    }
    if (viewId === 'view-policy' && !policyEditor) {
        policyEditor = new PolicyEditor('policy-editor-container');
    }
}

async function initNetworkMap() {
    try {
        networkMap = new NetworkMap('network-map-container');
        const response = await fetch(`${API_BASE}/infrastructure/topology`);
        const data = await response.json();
        networkMap.setData(data.nodes, data.links);
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
});
