
import { motion } from 'framer-motion';
import { Brain, Radio, ShieldCheck } from 'lucide-react';

const cards = [
    {
        title: "Decision Layer",
        subtitle: "Strategic Reliability",
        description: "Simulates 10,000+ scenarios/sec to predict grid stress 72 hours in advance.",
        icon: <Brain size={32} className="text-neon-cyan" />,
        delay: 0.1
    },
    {
        title: "Control Layer",
        subtitle: "Tactical Orchestration",
        description: "Managing frequency (Hz) and thermal-hydraulics for Bharat Small Reactors (BSR-220).",
        icon: <Radio size={32} className="text-neon-cyan" />,
        delay: 0.2
    },
    {
        title: "Infrastructure",
        subtitle: "Institutional Trust",
        description: "100% Transparency & Cyber-Kinetic Defense for Government Grids.",
        icon: <ShieldCheck size={32} className="text-neon-cyan" />,
        delay: 0.3
    }
];

export function TechCards() {
    return (
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {cards.map((card, index) => (
                <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: card.delay, duration: 0.5 }}
                    className="p-8 border border-light-gray/10 bg-black/40 backdrop-blur-md hover:border-neon-cyan/50 transition-all duration-300 group"
                >
                    <div className="mb-6 p-3 bg-neon-cyan/5 w-fit rounded-lg group-hover:bg-neon-cyan/10 transition-colors">
                        {card.icon}
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">{card.title}</h3>
                    <h4 className="text-sm font-mono text-neon-cyan mb-4">{card.subtitle}</h4>
                    <p className="text-light-gray leading-relaxed text-sm">{card.description}</p>
                </motion.div>
            ))}
        </section>
    );
}
