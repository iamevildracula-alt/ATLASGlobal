
import { Mail, MapPin, Phone } from 'lucide-react';

export function Founder() {
    return (
        <section className="flex flex-col md:flex-row gap-12 pt-12">
            <div className="flex-1 space-y-6">
                <h2 className="text-2xl font-bold mb-6 border-l-4 border-neon-cyan pl-4">Connect with the Architect.</h2>

                <div className="space-y-4 text-light-gray">
                    <p className="text-white text-lg font-bold">Paras Malhotra</p>
                    <p>Founder & Lead Architect, ATLASGlobal</p>

                    <div className="flex items-center gap-3 pt-4">
                        <MapPin size={18} className="text-neon-cyan" />
                        <span>Jind, Haryana, India</span>
                    </div>

                    <div className="flex items-center gap-3">
                        <Mail size={18} className="text-neon-cyan" />
                        <a href="mailto:iamparasmalhotra@gmail.com" className="hover:text-neon-cyan transition-colors">
                            iamparasmalhotra@gmail.com
                        </a>
                    </div>

                    <div className="flex items-center gap-3">
                        <Phone size={18} className="text-neon-cyan" />
                        <span>+91 7404322133</span>
                    </div>
                </div>
            </div>

            <div className="flex-1 bg-light-gray/5 p-8 border border-white/5 rounded-lg">
                <h3 className="text-lg font-bold text-white mb-4">Initial Consultation</h3>
                <p className="text-sm text-light-gray mb-6">
                    Schedule a 30-minute deep dive into our simulation architecture and grid integration protocols.
                </p>
                <form className="space-y-4">
                    <input
                        type="email"
                        placeholder="Enter your work email"
                        className="w-full bg-black/50 border border-light-gray/20 p-3 text-white focus:border-neon-cyan outline-none transition-colors"
                    />
                    <button className="w-full py-3 bg-neon-cyan/10 border border-neon-cyan text-neon-cyan font-bold hover:bg-neon-cyan hover:text-black transition-all duration-300">
                        REQUEST ACCESS
                    </button>
                </form>
            </div>
        </section>
    );
}
