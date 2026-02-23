
import { Hero } from './ui/Hero';
import { Simulation } from './ui/Simulation';
import { TechCards } from './ui/TechCards';
import { DeepDive } from './ui/DeepDive';
import { Founder } from './ui/Founder';

export function Overlay() {
    return (
        <div className="absolute top-0 left-0 w-full h-full overflow-y-auto z-50 scroll-smooth pointer-events-auto">
            <div className="max-w-7xl mx-auto px-6 py-12 flex flex-col gap-32 pointer-events-auto">
                <Hero />
                <Simulation />
                <TechCards />
                <DeepDive />
                <Founder />

                {/* Footer */}
                <footer className="text-center text-light-gray opacity-50 pb-32 text-sm border-t border-light-gray/5 pt-12">
                    <p className="mb-2">ATLASGlobal - Intelligent Grid Orchestration</p>
                    &copy; {new Date().getFullYear()} ATLASGlobal. All Systems Nominal.
                </footer>
            </div>
        </div>
    );
}
