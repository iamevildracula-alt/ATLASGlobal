
import { motion } from 'framer-motion';
import { ArrowRight, FileText } from 'lucide-react';

export function Hero() {
    return (
        <section className="min-h-[80vh] flex flex-col justify-center items-start pt-20">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="space-y-6 max-w-4xl"
            >
                <div className="inline-block px-3 py-1 border border-neon-cyan/30 rounded-full text-neon-cyan text-xs font-mono tracking-widest bg-neon-cyan/5 backdrop-blur-sm">
                    SYSTEM VERSION 220.4.1 // ONLINE
                </div>

                <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white leading-tight">
                    The Operating System for the <span className="text-transparent bg-clip-text bg-gradient-to-r from-neon-cyan to-white">Post-2026 Energy Grid</span>.
                </h1>

                <p className="text-xl text-light-gray max-w-2xl leading-relaxed">
                    Replacing "blind" legacy infrastructure with a predictive Decision & Control Layer for SMRs and Industrial Power.
                </p>

                <div className="flex flex-wrap gap-4 pt-4 relative" style={{ zIndex: 1000 }}>
                    <a
                        href="#simulation"
                        className="group relative px-8 py-4 bg-neon-cyan/30 border-2 border-neon-cyan text-neon-cyan font-bold tracking-wide overflow-hidden hover:bg-neon-cyan/40 transition-all duration-300 flex items-center gap-2 cursor-pointer"
                        style={{ pointerEvents: 'auto', position: 'relative', zIndex: 1001 }}
                        onClick={(e) => {
                            e.preventDefault();
                            console.log('VIEW SIMULATION clicked');
                            const target = document.getElementById('simulation');
                            if (target) {
                                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            }
                        }}
                    >
                        <span className="relative z-10 flex items-center gap-2">
                            VIEW SIMULATION <ArrowRight size={18} />
                        </span>
                        <div className="absolute inset-0 bg-neon-cyan/10 transform -skew-x-12 translate-x-full group-hover:translate-x-0 transition-transform duration-300" />
                    </a>

                    <a
                        href="https://docs.google.com/document/d/1pbKEerI7vuI88doSnE25u-PKT5OPvOshu1_tA6K5PCw/edit?usp=sharing"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-8 py-4 border-2 border-light-gray/50 text-light-gray hover:text-white hover:border-white hover:bg-white/10 transition-colors duration-300 flex items-center gap-2 cursor-pointer"
                        style={{ pointerEvents: 'auto', position: 'relative', zIndex: 1001 }}
                        onClick={(e) => {
                            console.log('READ TECHNICAL BRIEF clicked - URL:', e.currentTarget.href);
                        }}
                    >
                        <FileText size={18} /> READ TECHNICAL BRIEF
                    </a>
                </div>
            </motion.div>
        </section>
    );
}
