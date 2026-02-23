
interface DataPoint {
    timestamp: string;
    value: number;
}

export class HistoryChart {
    private container: HTMLElement;
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;
    private data: DataPoint[] = [];
    private label: string;
    private color: string;

    public refresh() {
        this.resize();
    }

    constructor(containerId: string, label: string, color: string) {
        this.container = document.getElementById(containerId) as HTMLElement;
        if (!this.container) throw new Error(`Container ${containerId} not found`);

        this.label = label;
        this.color = color;

        this.canvas = document.createElement('canvas');
        this.container.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d')!;

        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    private resize() {
        const rect = this.container.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.draw();
    }

    public setData(data: DataPoint[]) {
        this.data = data;
        this.draw();
    }

    private draw() {
        const w = this.canvas.width;
        const h = this.canvas.height;
        const pad = 40;

        this.ctx.clearRect(0, 0, w, h);

        if (this.data.length < 2) return;

        // Find min/max and slice last 24 points (last 24 hours) for detail view
        const displayData = this.data.slice(-24);

        const maxVal = Math.max(...displayData.map(d => d.value)) * 1.1;
        const minVal = Math.min(...displayData.map(d => d.value)) * 0.9;

        // Draw Axes
        this.ctx.beginPath();
        this.ctx.strokeStyle = '#444';
        this.ctx.lineWidth = 1;
        this.ctx.moveTo(pad, pad);
        this.ctx.lineTo(pad, h - pad);
        this.ctx.lineTo(w - pad, h - pad);
        this.ctx.stroke();

        // Draw Line
        this.ctx.beginPath();
        this.ctx.strokeStyle = this.color;
        this.ctx.lineWidth = 3;

        displayData.forEach((d, i) => {
            const x = pad + (i / (displayData.length - 1)) * (w - 2 * pad);
            const y = (h - pad) - ((d.value - minVal) / (maxVal - minVal)) * (h - 2 * pad);
            if (i === 0) this.ctx.moveTo(x, y);
            else this.ctx.lineTo(x, y);
        });

        this.ctx.stroke();

        // Label
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '14px Inter';
        this.ctx.fillText(this.label, pad + 10, pad + 20);
    }
}
