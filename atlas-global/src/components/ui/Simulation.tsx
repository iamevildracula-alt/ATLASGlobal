
import { motion } from 'framer-motion';
import { Activity, Cpu, Zap } from 'lucide-react';

export function Simulation() {
    return (
        <section className="space-y-8">
            <div className="flex flex-col md:flex-row justify-between items-end border-b border-light-gray/10 pb-4">
                <div>
                    <h2 className="text-3xl font-bold mb-2">Antigravity OS: Live BSR-220 Orchestration</h2>
                    <p className="text-light-gray text-sm font-mono">
                        REAL-TIME AUTONOMOUS RESPONSE // LATENCY: &lt;40MS
                    </p>
                </div>
                <div className="flex gap-6 text-sm font-mono text-neon-cyan mt-4 md:mt-0">
                    <div className="flex items-center gap-2"><Activity size={16} /> GRID STABLE</div>
                    <div className="flex items-center gap-2"><Cpu size={16} /> AI LOAD: 40%</div>
                    <div className="flex items-center gap-2"><Zap size={16} /> OUTPUT: 98.4%</div>
                </div>
            </div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
                className="relative aspect-video w-full bg-black/50 border border-light-gray/20 rounded-lg overflow-hidden backdrop-blur-sm group"
            >
                {/* Placeholder for Video - Replace with actual YouTube embed later */}
                <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-black to-deep-space/50">
                    <div className="text-center p-8 border border-neon-cyan/30 bg-black/80 backdrop-blur-md rounded-xl">
                        <p className="text-neon-cyan font-mono mb-4 text-lg">SYSTEM SIMULATION OFFLINE</p>
                        <p className="text-light-gray text-sm max-w-md">
                            Video feed connecting to secure server...
                            <br />
                            [INSERT_YOUR_VIDEO_LINK_HERE]
                        </p>
                    </div>

                    {/* Decorative UI elements for the "Control Screen" look */}
                    <div className="absolute top-4 left-4 w-32 h-32 border-l border-t border-neon-cyan/50 rounded-tl-lg" />
                    <div className="absolute bottom-4 right-4 w-32 h-32 border-r border-b border-neon-cyan/50 rounded-br-lg" />
                    <div className="absolute top-1/2 left-4 w-1 h-12 bg-neon-cyan/30" />
                    <div className="absolute top-1/2 right-4 w-1 h-12 bg-neon-cyan/30" />
                </div>
            </motion.div>
        </section>
    );
}
