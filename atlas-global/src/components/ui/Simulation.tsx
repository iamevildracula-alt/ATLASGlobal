
import { motion } from 'framer-motion';
import { Activity, Cpu, Zap } from 'lucide-react';

export function Simulation() {
    return (
        <section id="simulation" className="space-y-8 scroll-mt-20">
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
                <div className="absolute inset-0 flex items-center justify-center bg-black/80">
                    <iframe
                        src="https://drive.google.com/file/d/1psit8CmzDRe_RVnns0m0cStex6ynqjR9/preview"
                        className="w-full h-full border-none z-0"
                        allow="autoplay; fullscreen"
                        allowFullScreen
                        title="Antigravity OS Simulation"
                    />

                    {/* Security Layer - Decorative only, must not block iframe */}
                    <div className="absolute inset-0 pointer-events-none border border-neon-cyan/20 rounded-lg z-10" />

                    {/* Fallback link if iframe is blocked by browser privacy settings */}
                    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/80 px-4 py-2 rounded-full border border-neon-cyan/30 z-20">
                        <a
                            href="https://drive.google.com/file/d/1psit8CmzDRe_RVnns0m0cStex6ynqjR9/view?usp=sharing"
                            target="_blank"
                            className="text-neon-cyan text-xs font-mono hover:underline"
                        >
                            EXTERNAL VIDEO FEED ➜
                        </a>
                    </div>
                </div>

                {/* Decorative UI elements for the "Control Screen" look */}
                <div className="absolute top-4 left-4 w-32 h-32 border-l border-t border-neon-cyan/50 rounded-tl-lg pointer-events-none" />
                <div className="absolute bottom-4 right-4 w-32 h-32 border-r border-b border-neon-cyan/50 rounded-br-lg pointer-events-none" />
                <div className="absolute top-1/2 left-4 w-1 h-12 bg-neon-cyan/30 pointer-events-none" />
                <div className="absolute top-1/2 right-4 w-1 h-12 bg-neon-cyan/30 pointer-events-none" />
            </motion.div>
        </section>
    );
}
