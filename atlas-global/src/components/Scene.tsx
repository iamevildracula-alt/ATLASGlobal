
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { NeuralNetwork } from './NeuralNetwork';
import { EffectComposer, Bloom } from '@react-three/postprocessing';

export function Scene() {
    return (
        <Canvas camera={{ position: [0, 0, 15], fov: 60 }} gl={{ alpha: true }}>
            {/* Transparent background */}

            {/* Lighting */}
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} intensity={1} color="#00F0FF" />

            {/* Objects */}
            <NeuralNetwork />
            <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
            <fog attach="fog" args={['#030712', 10, 25]} />

            {/* Effects */}
            <EffectComposer>
                <Bloom luminanceThreshold={0.05} luminanceSmoothing={0.9} height={300} intensity={2} />
            </EffectComposer>

            {/* Controls */}
            <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.3} />
        </Canvas>
    );
}
