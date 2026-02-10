
const API_BASE = 'http://localhost:8000/api';

export class PolicyEditor {
    private container: HTMLElement;

    constructor(containerId: string) {
        this.container = document.getElementById(containerId) as HTMLElement;
        if (!this.container) throw new Error(`Container ${containerId} not found`);
        this.render();
        this.fetchPolicy();
    }

    private render() {
        this.container.innerHTML = `
            <div class="policy-form" style="max-width: 600px; background: #1a1a1a; padding: 2rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
                <div class="form-group" style="margin-bottom: 1.5rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Max Cost ($/MWh)</label>
                    <input type="number" id="pol-cost" value="100" style="width: 100%; padding: 0.5rem; background: #333; border: 1px solid #444; color: white; border-radius: 6px;">
                </div>
                
                <div class="form-group" style="margin-bottom: 1.5rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Max Carbon Intensity (t/MWh)</label>
                    <input type="number" id="pol-carbon" value="0.5" step="0.1" style="width: 100%; padding: 0.5rem; background: #333; border: 1px solid #444; color: white; border-radius: 6px;">
                </div>

                <div class="form-group" style="margin-bottom: 1.5rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Min Reliability Score (0.0 - 1.0)</label>
                    <input type="range" id="pol-rel" min="0.8" max="1.0" step="0.01" value="0.99" style="width: 100%;">
                    <span id="pol-rel-val" style="float: right; color: var(--text-dim);">0.99</span>
                </div>
                
                <div class="form-group" style="margin-bottom: 2rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Risk Tolerance</label>
                    <select id="pol-risk" style="width: 100%; padding: 0.5rem; background: #333; border: 1px solid #444; color: white; border-radius: 6px;">
                        <option value="averse">Risk Averse</option>
                        <option value="neutral">Neutral</option>
                        <option value="seeking">Risk Seeking</option>
                    </select>
                </div>

                <button id="pol-save" class="btn-primary" style="width: 100%; padding: 0.75rem; background: var(--primary); color: white; border: none; border-radius: 6px; font-weight: 600; cursor: pointer;">
                    Update Policy
                </button>
                <div id="pol-status" style="margin-top: 1rem; text-align: center; font-size: 0.9rem;"></div>
            </div>
        `;

        // Event Listeners
        const range = document.getElementById('pol-rel') as HTMLInputElement;
        const val = document.getElementById('pol-rel-val');
        if (range && val) {
            range.oninput = () => val.innerText = range.value;
        }

        const btn = document.getElementById('pol-save');
        if (btn) btn.onclick = () => this.savePolicy();
    }

    async fetchPolicy() {
        try {
            const res = await fetch(`${API_BASE}/policy/`);
            const data = await res.json();

            (document.getElementById('pol-cost') as HTMLInputElement).value = data.max_cost_per_mwh;
            (document.getElementById('pol-carbon') as HTMLInputElement).value = data.max_carbon_per_mwh;
            (document.getElementById('pol-rel') as HTMLInputElement).value = data.min_reliability_score;
            (document.getElementById('pol-risk') as HTMLSelectElement).value = data.risk_tolerance;

            const val = document.getElementById('pol-rel-val');
            if (val) val.innerText = data.min_reliability_score;

        } catch (e) {
            console.error('Failed to fetch policy', e);
        }
    }

    async savePolicy() {
        const payload = {
            max_cost_per_mwh: parseFloat((document.getElementById('pol-cost') as HTMLInputElement).value),
            max_carbon_per_mwh: parseFloat((document.getElementById('pol-carbon') as HTMLInputElement).value),
            min_reliability_score: parseFloat((document.getElementById('pol-rel') as HTMLInputElement).value),
            risk_tolerance: (document.getElementById('pol-risk') as HTMLSelectElement).value
        };

        const status = document.getElementById('pol-status');
        if (status) status.innerText = 'Saving...';

        try {
            const res = await fetch(`${API_BASE}/policy/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                if (status) {
                    status.innerText = 'Policy Updated Successfully';
                    status.style.color = '#51cf66';
                }
            } else {
                if (status) {
                    status.innerText = 'Error Saving Policy';
                    status.style.color = '#ff6b6b';
                }
            }
        } catch (e) {
            console.error(e);
            if (status) {
                status.innerText = 'Network Error';
                status.style.color = '#ff6b6b';
            }
        }
    }
}
