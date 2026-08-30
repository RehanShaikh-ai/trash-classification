import React, { useState, useEffect } from "react";
import { Terminal, Sparkles } from "lucide-react";

interface NavbarProps {
  onOpenContractModal: () => void;
  isMockMode: boolean;
  setIsMockMode: (val: boolean) => void;
  apiConnected: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenContractModal,
  isMockMode,
  setIsMockMode,
  apiConnected,
}) => {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 40) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 w-full transition-all duration-300 ${
        isScrolled
          ? "bg-[#080d19]/70 backdrop-blur-xl border-b border-white/10 py-3.5 shadow-2xl"
          : "bg-transparent py-6"
      }`}
    >
      <nav className="mx-auto max-w-7xl px-6 sm:px-12 flex items-center justify-between">
        {/* Brand Logo matching Velorah */}
        <div className="flex items-center gap-2">
          <a href="#" className="flex items-baseline gap-0.5 group">
            <span className="font-serif text-3xl sm:text-4xl tracking-tight text-white group-hover:text-[#eaa7a3] transition-colors">
              EcoSort
            </span>
            <sup className="text-[0.45em] font-serif text-white/80">®</sup>
          </a>
        </div>

        {/* Center Nav Links directly on sky */}
        <div className="hidden md:flex items-center gap-10 text-sm text-white/85 font-normal tracking-wide">
          <a
            href="#classifier"
            className="hover:text-white transition-colors drop-shadow"
          >
            Classifier
          </a>
          <a
            href="#categories"
            className="hover:text-white transition-colors drop-shadow"
          >
            Categories
          </a>
          <button
            type="button"
            onClick={onOpenContractModal}
            className="flex items-center gap-1.5 hover:text-white transition-colors cursor-pointer drop-shadow"
          >
            <Terminal className="h-3.5 w-3.5 text-[#eaa7a3]" />
            <span>Contract v1.0.0</span>
          </button>
        </div>

        {/* Action Buttons: Status Pill & Velorah Glass Pill */}
        <div className="flex items-center gap-3.5">
          {/* Status Mode Pill */}
          <button
            type="button"
            onClick={() => setIsMockMode(!isMockMode)}
            title={isMockMode ? "Switch to Live Flask Backend (http://localhost:5000)" : "Switch to Mock API Simulator"}
            className="velorah-pill px-3.5 py-1.5 rounded-full flex items-center gap-2 text-xs font-mono transition-all hover:border-[#eaa7a3]/50 cursor-pointer text-white/90"
          >
            <span className="relative flex h-2 w-2">
              <span
                className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                  isMockMode ? "bg-[#eaa7a3]" : apiConnected ? "bg-emerald-400" : "bg-rose-400"
                }`}
              />
              <span
                className={`relative inline-flex rounded-full h-2 w-2 ${
                  isMockMode ? "bg-[#eaa7a3]" : apiConnected ? "bg-emerald-400" : "bg-rose-400"
                }`}
              />
            </span>
            <span className="hidden sm:inline">
              {isMockMode ? "Mock Mode" : apiConnected ? "Live API (5000)" : "Backend Offline"}
            </span>
          </button>

          {/* Velorah-style Pill Button */}
          <a
            href="#classifier"
            className="velorah-btn-primary rounded-full px-6 sm:px-8 py-2.5 text-xs sm:text-sm font-normal text-white tracking-wide transition-all hover:scale-105 active:scale-95 cursor-pointer shadow-lg"
          >
            <span className="flex items-center gap-1.5">
              <Sparkles className="h-3.5 w-3.5 text-[#eaa7a3]" />
              Scan Waste
            </span>
          </a>
        </div>
      </nav>
    </header>
  );
};
