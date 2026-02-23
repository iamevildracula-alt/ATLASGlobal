import * as THREE from 'three';

interface Node {
    id: string;
    name: string;
    type: string;
    capacity_mw: number;
    location_x: number;
    location_y: number;
    location_z: number;
    status: string;
}

interface Link {
    id: string;
    source_id: string;
    target_id: string;
    capacity_mw: number;
    current_load_mw: number;
    resistance: number;
    reactance: number;
    length_km: number;
    fault_position: number | null;
    status: string;
}

export type ViewDimension = '1D' | '2D' | '3D';

export class DigitalTwinMap {
    private container: HTMLElement;
    private scene!: THREE.Scene;
    private camera!: THREE.Camera;
    private nodes: Node[] = [];
    private links: Link[] = [];
    private dimension: ViewDimension = '2D';

    private nodeObjects: Map<string, THREE.Object3D> = new Map();
    private linkObjects: Map<string, { line: THREE.Line, particles: THREE.Points }> = new Map();
    private nodeHealthMarkers: Map<string, THREE.Mesh> = new Map();

    private map: any;
    private threeLayer: any;

    constructor(containerId: string) {
        this.container = document.getElementById(containerId) as HTMLElement;
        if (!this.container) throw new Error(`Container ${containerId} not found`);

        const maplibregl = (window as any).maplibregl;
        const ThreeLayer = (window as any).ThreeLayer ||
            ((window as any).maplibreglThree && (window as any).maplibreglThree.ThreeLayer) ||
            ((window as any).maplibregl_three && (window as any).maplibregl_three.ThreeLayer);

        this.map = new maplibregl.Map({
            container: containerId,
            style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
            center: [77.580, 12.950], // Bangalore
            zoom: 12,
            pitch: 60,
            antialias: true
        });

        this.map.on('style.load', () => {
            this.threeLayer = new ThreeLayer('threejs-layer');
            this.scene = this.threeLayer.getScene();
            this.camera = this.threeLayer.getCamera();

            this.map.addLayer(this.threeLayer);

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
            this.scene.add(ambientLight);

            // Important: Use the map's container for the glass effect if needed
            this.container.classList.add('maplibre-glass-ui');

            this.animate();
        });
    }

    private rebuildScene() {
        if (!this.scene) return;

        this.nodeObjects.forEach(obj => this.scene.remove(obj));
        this.linkObjects.forEach(obj => {
            this.scene.remove(obj.line);
            this.scene.remove(obj.particles);
        });
        this.nodeHealthMarkers.forEach(obj => this.scene.remove(obj));

        this.nodeObjects.clear();
        this.linkObjects.clear();
        this.nodeHealthMarkers.clear();

        const maplibregl = (window as any).maplibregl;

        this.nodes.forEach(node => {
            const coords = maplibregl.MercatorCoordinate.fromLngLat([node.location_x, node.location_y], 0);
            const z = this.dimension === '3D' ? node.location_z / 100000 : 0;

            const geo = node.type === 'nuclear' ? new THREE.TorusKnotGeometry(0.0001, 0.00003, 64, 8) : new THREE.SphereGeometry(0.00008, 16, 16);
            const mat = new THREE.MeshStandardMaterial({
                color: this.getNodeColor(node.type),
                emissive: this.getNodeColor(node.type),
                emissiveIntensity: 0.5
            });
            const mesh = new THREE.Mesh(geo, mat);
            mesh.position.set(coords.x, coords.y, coords.z + z);
            this.scene.add(mesh);
            this.nodeObjects.set(node.id, mesh);

            const healthGeo = new THREE.RingGeometry(0.0001, 0.00012, 16);
            const healthMat = new THREE.MeshBasicMaterial({ color: 0x00ff00, side: THREE.DoubleSide, transparent: true, opacity: 0.8 });
            const healthRing = new THREE.Mesh(healthGeo, healthMat);
            healthRing.position.set(coords.x, coords.y, coords.z + z);
            this.scene.add(healthRing);
            this.nodeHealthMarkers.set(node.id, healthRing);
        });

        this.links.forEach(link => {
            const startNode = this.nodes.find(n => n.id === link.source_id);
            const endNode = this.nodes.find(n => n.id === link.target_id);
            if (!startNode || !endNode) return;

            const startCoords = maplibregl.MercatorCoordinate.fromLngLat([startNode.location_x, startNode.location_y], 0);
            const endCoords = maplibregl.MercatorCoordinate.fromLngLat([endNode.location_x, endNode.location_y], 0);

            const material = new THREE.LineBasicMaterial({
                color: link.status === 'failed' ? 0xff4d4d : 0x4dabf7,
                transparent: true,
                opacity: 0.6
            });

            const points = [
                new THREE.Vector3(startCoords.x, startCoords.y, startCoords.z + (this.dimension === '3D' ? startNode.location_z / 100000 : 0)),
                new THREE.Vector3(endCoords.x, endCoords.y, endCoords.z + (this.dimension === '3D' ? endNode.location_z / 100000 : 0))
            ];

            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const line = new THREE.Line(geometry, material);
            this.scene.add(line);

            const flowGeo = new THREE.BufferGeometry();
            const flowCount = 5;
            const flowPos = new Float32Array(flowCount * 3);
            for (let i = 0; i < flowCount; i++) {
                const alpha = i / flowCount;
                flowPos[i * 3] = startCoords.x + (endCoords.x - startCoords.x) * alpha;
                flowPos[i * 3 + 1] = startCoords.y + (endCoords.y - startCoords.y) * alpha;
                flowPos[i * 3 + 2] = (startCoords.z + (this.dimension === '3D' ? startNode.location_z / 100000 : 0)) +
                    ((endCoords.z + (this.dimension === '3D' ? endNode.location_z / 100000 : 0)) - (startCoords.z + (this.dimension === '3D' ? startNode.location_z / 100000 : 0))) * alpha;
            }
            flowGeo.setAttribute('position', new THREE.BufferAttribute(flowPos, 3));
            const flowMat = new THREE.PointsMaterial({ color: 0x4dabf7, size: 2, sizeAttenuation: false, transparent: true, opacity: 0.8 });
            const flowParticles = new THREE.Points(flowGeo, flowMat);

            const loadRatio = Math.min(1.0, link.current_load_mw / (link.capacity_mw || 1));
            (flowParticles as any).flowSpeed = 0.005 + loadRatio * 0.05;

            this.scene.add(flowParticles);
            this.linkObjects.set(link.id, { line, particles: flowParticles });

            if (link.status === 'failed' && link.fault_position !== null) {
                this.addFaultMarker(startNode, endNode, link.fault_position);
            }
        });
    }

    private animate() {
        requestAnimationFrame(() => this.animate());
        if (this.map && this.map.loaded()) this.map.triggerRepaint();

        this.linkObjects.forEach((obj, id) => {
            const link = this.links.find(l => l.id === id);
            if (!link || link.status === 'failed') {
                obj.particles.visible = false;
                return;
            }
            obj.particles.visible = true;
            const pos = obj.particles.geometry.attributes.position.array as Float32Array;
            const startNode = this.nodes.find(n => n.id === link.source_id)!;
            const endNode = this.nodes.find(n => n.id === link.target_id)!;
            const speed = (obj.particles as any).flowSpeed || 0.01;

            const maplibregl = (window as any).maplibregl;
            const sc = maplibregl.MercatorCoordinate.fromLngLat([startNode.location_x, startNode.location_y], 0);
            const ec = maplibregl.MercatorCoordinate.fromLngLat([endNode.location_x, endNode.location_y], 0);
            const sz = sc.z + (this.dimension === '3D' ? startNode.location_z / 100000 : 0);
            const ez = ec.z + (this.dimension === '3D' ? endNode.location_z / 100000 : 0);

            for (let i = 0; i < pos.length / 3; i++) {
                let alpha = (Date.now() * speed + i * 200) % 1000 / 1000;
                pos[i * 3] = sc.x + (ec.x - sc.x) * alpha;
                pos[i * 3 + 1] = sc.y + (ec.y - sc.y) * alpha;
                pos[i * 3 + 2] = sz + (ez - sz) * alpha;
            }
            obj.particles.geometry.attributes.position.needsUpdate = true;
        });

        this.nodeHealthMarkers.forEach((marker) => {
            const s = 1 + Math.sin(Date.now() * 0.003) * 0.2;
            marker.scale.set(s, s, s);
            (marker.material as THREE.MeshBasicMaterial).opacity = 0.8 - Math.sin(Date.now() * 0.003) * 0.3;
        });
    }

    private addFaultMarker(start: Node, end: Node, position: number) {
        if (!this.scene) return;
        const maplibregl = (window as any).maplibregl;
        const sc = maplibregl.MercatorCoordinate.fromLngLat([start.location_x, start.location_y], 0);
        const ec = maplibregl.MercatorCoordinate.fromLngLat([end.location_x, end.location_y], 0);
        const sz = sc.z + (this.dimension === '3D' ? start.location_z / 100000 : 0);
        const ez = ec.z + (this.dimension === '3D' ? end.location_z / 100000 : 0);

        const fx = sc.x + (ec.x - sc.x) * position;
        const fy = sc.y + (ec.y - sc.y) * position;
        const fz = sz + (ez - sz) * position;

        const geo = new THREE.SphereGeometry(0.0001, 12, 12);
        const mat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
        const marker = new THREE.Mesh(geo, mat);
        marker.position.set(fx, fy, fz);
        this.scene.add(marker);
    }

    private getNodeColor(type: string): number {
        switch (type) {
            case 'generator': return 0xffd43b;
            case 'load': return 0xced4da;
            case 'storage': return 0x51cf66;
            case 'nuclear': return 0x8b5cf6;
            default: return 0xffffff;
        }
    }

    public setData(nodes: Node[], links: Link[]) {
        this.nodes = nodes;
        this.links = links;
        this.rebuildScene();
    }

    public setDimension(dim: ViewDimension) {
        this.dimension = dim;
        this.rebuildScene();
    }

    public refresh() {
        if (this.map) this.map.resize();
        this.rebuildScene();
    }
}
