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

    // Update Live Telemetry Log
    const logEl = document.getElementById('live-telemetry-log');
    if (logEl) {
        const timeStr = new Date().toLocaleTimeString();
        let logMsg = `[${timeStr}] SYNC: ${JSON.stringify(data)}`;

        // If it's a Weather or Market packet, update specific UI cards too
        if (data.data_type === 'weather') {
            const weatherEl = document.getElementById('live-weather-feed');
            if (weatherEl) weatherEl.innerHTML = `Temp: ${data.temp_c}°C<br>Wind: ${data.wind_kph}km/h`;
            logMsg = `[${timeStr}] L1 INGEST (WEATHER): ${data.temp_c}°C, ${data.condition}`;
        } else if (data.data_type === 'market') {
            const marketEl = document.getElementById('live-market-feed');
            if (marketEl) marketEl.innerHTML = `$${data.price_mwh}/MWh<br>Grid: ${data.region}`;
            logMsg = `[${timeStr}] L1 INGEST (MARKET): $${data.price_mwh}/MWh`;
        }

        const newLog = document.createElement('div');
        newLog.innerText = logMsg;
        if (data.is_verified === false) {
            newLog.style.color = '#ff4d4d'; // Red for adversarial/drift blocks
        }

        logEl.prepend(newLog);

        // Keep log bounded
        if (logEl.children.length > 50) {
            logEl.removeChild(logEl.lastChild as Node);
        }
    }

    // Update map if available
    if (networkMap) {
        // networkMap.updateTelemetry(data); // Future enhancement
    }
}

// Scenario Logic Removed - Sentient Grid now relies entirely on Live Real-Time Ingestion (L1)

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
