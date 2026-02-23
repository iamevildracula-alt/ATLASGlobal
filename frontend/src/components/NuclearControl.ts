export class NuclearControl {
    private containerId: string;
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D | null;
    private state: {
        temp: number;
        pressure: number;
        margin: number;
        scram: boolean;
    };

    constructor(containerId: string) {
        this.containerId = containerId;
        this.state = { temp: 285, pressure: 15.5, margin: 100, scram: false };

        const container = document.getElementById(containerId);
        if (!container) throw new Error(`Container ${containerId} not found`);

        this.canvas = document.createElement('canvas');
        this.canvas.width = 400;
        this.canvas.height = 400;
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        container.appendChild(this.canvas);

        this.ctx = this.canvas.getContext('2d');
        this.render();
    }

    public updateState(temp: number, pressure: number, margin: number, scram: boolean) {
        this.state = { temp, pressure, margin, scram };

        // Update DOM elements
        const tempEl = document.getElementById('nuclear-temp');
        if (tempEl) tempEl.innerText = `${temp.toFixed(1)} °C`;

        const pressEl = document.getElementById('nuclear-pressure');
        if (pressEl) pressEl.innerText = `${pressure.toFixed(2)} MPa`;

        const marginEl = document.getElementById('nuclear-margin');
        if (marginEl) {
            marginEl.innerText = `${(margin * 100).toFixed(1)} %`;
            marginEl.style.color = margin < 0.2 ? '#ff6b6b' : '#51cf66';
        }

        const scramOverlay = document.getElementById('nuclear-scram-overlay');
        if (scramOverlay) {
            scramOverlay.style.display = scram ? 'flex' : 'none';
        }

        this.render();
    }

    private render() {
        if (!this.ctx) return;
        const { width, height } = this.canvas;
        const ctx = this.ctx;

        ctx.clearRect(0, 0, width, height);
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) * 0.4;

        // Draw Temperature Gauge
        this.drawGauge(ctx, centerX, centerY, radius, this.state.temp, 200, 800, 'Core Temperature', '°C');
    }

    private drawGauge(ctx: CanvasRenderingContext2D, x: number, y: number, r: number, val: number, min: number, max: number, label: string, unit: string) {
        // Outer track
        ctx.beginPath();
        ctx.arc(x, y, r, 0.75 * Math.PI, 2.25 * Math.PI);
        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        ctx.lineWidth = 15;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Value arc
        const pct = (val - min) / (max - min);
        const endAngle = 0.75 * Math.PI + (pct * 1.5 * Math.PI);

        ctx.beginPath();
        ctx.arc(x, y, r, 0.75 * Math.PI, endAngle);

        // Color based on danger
        if (pct < 0.6) ctx.strokeStyle = '#51cf66';
        else if (pct < 0.85) ctx.strokeStyle = '#fcc419';
        else ctx.strokeStyle = '#ff6b6b';

        ctx.stroke();

        // Text
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 32px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(`${val.toFixed(0)}`, x, y);

        ctx.font = '14px Inter';
        ctx.fillStyle = 'rgba(255,255,255,0.5)';
        ctx.fillText(unit, x, y + 25);

        ctx.font = '12px Inter';
        ctx.fillText(label.toUpperCase(), x, y - 40);
    }
}
