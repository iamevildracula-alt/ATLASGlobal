
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

                <div className="flex flex-wrap gap-4 pt-4">
                    <button className="group relative px-8 py-4 bg-neon-cyan/10 border border-neon-cyan/50 text-neon-cyan font-bold tracking-wide overflow-hidden hover:bg-neon-cyan/20 transition-all duration-300">
                        <span className="relative z-10 flex items-center gap-2">
                            VIEW SIMULATION <ArrowRight size={18} />
                        </span>
                        <div className="absolute inset-0 bg-neon-cyan/10 transform -skew-x-12 translate-x-full group-hover:translate-x-0 transition-transform duration-300" />
                    </button>

                    <button className="px-8 py-4 border border-light-gray/30 text-light-gray hover:text-white hover:border-white transition-colors duration-300 flex items-center gap-2">
                        <FileText size={18} /> READ TECHNICAL BRIEF
                    </button>
                </div>
            </motion.div>
        </section>
    );
}
