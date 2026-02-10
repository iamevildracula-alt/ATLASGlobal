
import { Hero } from './ui/Hero';
import { Simulation } from './ui/Simulation';
import { TechCards } from './ui/TechCards';
import { DeepDive } from './ui/DeepDive';
import { Founder } from './ui/Founder';

export function Overlay() {
    return (
        <div className="absolute top-0 left-0 w-full h-full overflow-y-auto z-10 scroll-smooth">
            <div className="max-w-7xl mx-auto px-6 py-12 flex flex-col gap-32">
                <Hero />
                <Simulation />
                <TechCards />
                <DeepDive />
                <Founder />

                {/* Footer */}
                <footer className="text-center text-light-gray opacity-50 pb-12 text-sm">
                    &copy; {new Date().getFullYear()} ATLASGlobal. All Systems Nominal.
                </footer>
            </div>
        </div>
    );
}
