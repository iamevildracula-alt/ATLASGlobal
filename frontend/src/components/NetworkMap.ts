
interface Node {
    id: string;
    name: string;
    type: string;
    capacity_mw: number;
    location_x: number;
    location_y: number;
    status: string;
}

interface Link {
    id: string;
    source_id: string;
    target_id: string;
    capacity_mw: number;
    current_load_mw: number;
    status: string;
}

export class NetworkMap {
    private container: HTMLElement;
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;
    private nodes: Node[] = [];
    private links: Link[] = [];

    public refresh() {
        this.resize();
    }

    constructor(containerId: string) {
        this.container = document.getElementById(containerId) as HTMLElement;
        if (!this.container) throw new Error(`Container ${containerId} not found`);

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

    public setData(nodes: Node[], links: Link[]) {
        this.nodes = nodes;
        this.links = links;
        this.draw();
    }

    private draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw Links
        this.links.forEach(link => {
            const source = this.nodes.find(n => n.id === link.source_id);
            const target = this.nodes.find(n => n.id === link.target_id);
            if (source && target) {
                this.drawLink(source, target, link);
            }
        });

        // Draw Nodes
        this.nodes.forEach(node => this.drawNode(node));
    }

    private drawLink(source: Node, target: Node, link: Link) {
        const sx = (source.location_x / 100) * this.canvas.width;
        const sy = (source.location_y / 100) * this.canvas.height;
        const tx = (target.location_x / 100) * this.canvas.width;
        const ty = (target.location_y / 100) * this.canvas.height;

        this.ctx.beginPath();
        this.ctx.moveTo(sx, sy);
        this.ctx.lineTo(tx, ty);

        const loadRatio = link.current_load_mw / link.capacity_mw;
        this.ctx.lineWidth = 2 + (loadRatio * 4);
        this.ctx.strokeStyle = loadRatio > 0.9 ? '#ff4d4d' : '#4dabf7'; // Red if overloaded
        this.ctx.globalAlpha = 0.6;
        this.ctx.stroke();
        this.ctx.globalAlpha = 1.0;
    }

    private drawNode(node: Node) {
        const x = (node.location_x / 100) * this.canvas.width;
        const y = (node.location_y / 100) * this.canvas.height;

        this.ctx.beginPath();
        this.ctx.arc(x, y, 10, 0, Math.PI * 2);

        let color = '#ffffff';
        switch (node.type) {
            case 'generator': color = '#ffd43b'; break; // Yellow
            case 'load': color = '#ced4da'; break; // Gray
            case 'storage': color = '#51cf66'; break; // Green
            case 'nuclear': color = '#8b5cf6'; break; // Purple
        }

        this.ctx.fillStyle = color;
        this.ctx.fill();
        this.ctx.strokeStyle = '#fff';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();

        // Label
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '10px Inter';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(node.name, x, y + 20);
    }
}
