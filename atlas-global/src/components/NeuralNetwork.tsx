
import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const count = 400;
const radius = 12;
const maxConnections = 1200;

export function NeuralNetwork() {
    const meshRef = useRef<THREE.InstancedMesh>(null);
    const lineGeometryRef = useRef<THREE.BufferGeometry>(null);
    const groupRef = useRef<THREE.Group>(null);

    // Initial positions and randomized data
    const particles = useMemo(() => {
        const temp = [];
        for (let i = 0; i < count; i++) {
            temp.push({
                pos: new THREE.Vector3(
                    (Math.random() - 0.5) * radius * 2.5,
                    (Math.random() - 0.5) * radius * 2,
                    (Math.random() - 0.5) * radius * 2.5
                ),
                offset: Math.random() * Math.PI * 2,
                speed: 0.1 + Math.random() * 0.15
            });
        }
        return temp;
    }, []);

    const lineBuffer = useMemo(() => new Float32Array(maxConnections * 2 * 3), []);
    const dummy = useMemo(() => new THREE.Object3D(), []);

    useFrame((state) => {
        const t = state.clock.getElapsedTime();
        const positions: THREE.Vector3[] = [];

        particles.forEach((p, i) => {
            // Fluid waving motion
            const waveX = Math.sin(t * p.speed + p.offset) * 0.8;
            const waveY = Math.cos(t * p.speed * 0.7 + p.offset) * 0.8;
            const waveZ = Math.sin(t * p.speed * 1.3 + p.offset) * 0.8;

            const currentPos = p.pos.clone().add(new THREE.Vector3(waveX, waveY, waveZ));
            positions.push(currentPos);

            dummy.position.copy(currentPos);
            dummy.scale.setScalar(0.8 + Math.sin(t * 2 + p.offset) * 0.2); // Pulse effect
            dummy.updateMatrix();
            if (meshRef.current) {
                meshRef.current.setMatrixAt(i, dummy.matrix);
            }
        });

        if (meshRef.current) meshRef.current.instanceMatrix.needsUpdate = true;

        // Connections logic
        if (lineGeometryRef.current) {
            let lineIndex = 0;
            for (let i = 0; i < count && lineIndex < maxConnections; i++) {
                for (let j = i + 1; j < count && lineIndex < maxConnections; j++) {
                    const distSq = positions[i].distanceToSquared(positions[j]);
                    if (distSq < 16) { // distance < 4
                        lineBuffer[lineIndex * 6] = positions[i].x;
                        lineBuffer[lineIndex * 6 + 1] = positions[i].y;
                        lineBuffer[lineIndex * 6 + 2] = positions[i].z;
                        lineBuffer[lineIndex * 6 + 3] = positions[j].x;
                        lineBuffer[lineIndex * 6 + 4] = positions[j].y;
                        lineBuffer[lineIndex * 6 + 5] = positions[j].z;
                        lineIndex++;
                    }
                }
            }

            lineGeometryRef.current.setAttribute('position', new THREE.BufferAttribute(lineBuffer.subarray(0, lineIndex * 6), 3));
        }

        if (groupRef.current) {
            groupRef.current.rotation.y = t * 0.015;
            groupRef.current.rotation.z = Math.sin(t * 0.1) * 0.05;
        }
    });

    return (
        <group ref={groupRef}>
            <instancedMesh ref={meshRef} args={[undefined, undefined, count]}>
                <sphereGeometry args={[0.06, 12, 12]} />
                <meshBasicMaterial color="#00F0FF" transparent opacity={0.7} />
            </instancedMesh>

            <lineSegments>
                <bufferGeometry ref={lineGeometryRef} />
                <lineBasicMaterial color="#00D4FF" transparent opacity={0.12} />
            </lineSegments>
        </group>
    );
}
