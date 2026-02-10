
import { motion } from 'framer-motion';
import { Download } from 'lucide-react';

export function DeepDive() {
    return (
        <section className="py-12 border-y border-light-gray/10 relative overflow-hidden">
            {/* Background Accent */}
            <div className="absolute top-0 right-0 w-1/3 h-full bg-neon-cyan/5 skew-x-12 transform translate-x-32" />

            <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-10">
                <div className="max-w-xl space-y-4">
                    <h2 className="text-3xl font-bold text-white">Built on First-Principles Physics.</h2>
                    <p className="text-light-gray leading-relaxed">
                        Our logic engine is constrained by the laws of thermodynamics, not just statistical probability.
                        Download the full technical analysis.
                    </p>
                </div>

                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 bg-white text-black font-bold flex items-center gap-3 hover:bg-neon-cyan hover:text-black transition-colors duration-300"
                >
                    <Download size={20} />
                    DOWNLOAD WHITE PAPER (PDF)
                </motion.button>
            </div>
        </section>
    );
}
