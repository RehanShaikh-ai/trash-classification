import React from "react";
import { Cpu, ShieldCheck } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-white/10 bg-[#060a14] py-14 px-4 sm:px-8 mt-24">
      <div className="mx-auto max-w-7xl flex flex-col md:flex-row items-center justify-between gap-6">
        {/* Brand & Contract Attribution */}
        <div className="flex flex-col sm:flex-row items-center gap-4 text-center sm:text-left">
          <div className="h-9 w-9 rounded-xl velorah-pill flex items-center justify-center text-[#eaa7a3]">
            <Cpu className="h-4 w-4" />
          </div>
          <div>
            <p className="font-serif text-xl text-white font-normal">EcoSort Intelligence</p>
            <p className="text-xs font-mono text-white/60">
              Technical Interface Contract v1.0.0 • React 19 + Vite + Tailwind v4 + Flask PyTorch
            </p>
          </div>
        </div>

        {/* Badges */}
        <div className="flex items-center gap-4 text-xs font-mono text-white/60">
          <span className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full velorah-pill">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            Zero Direct Model Coupling
          </span>
          <span className="px-3.5 py-1.5 rounded-full velorah-pill">
            RGB 224×224
          </span>
        </div>
      </div>
    </footer>
  );
};
