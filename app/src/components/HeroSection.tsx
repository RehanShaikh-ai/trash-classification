import React from "react";
import { ArrowDown } from "lucide-react";

interface HeroSectionProps {
  onStartClick: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onStartClick }) => {
  return (
    <section className="relative min-h-screen h-screen w-full overflow-hidden flex flex-col justify-between pt-24 pb-12 px-4 sm:px-8">
      {/* Background Sunset Clouds Video & Ethereal Overlays */}
      <div className="absolute inset-0 z-0 overflow-hidden">
        <video
          className="h-full w-full object-cover opacity-90 scale-105 filter contrast-105 brightness-100"
          src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260324_151826_c7218672-6e92-402c-9e45-f1e0f454bdc4.mp4"
          autoPlay
          loop
          muted
          playsInline
        />
        {/* Soft Vignettes: subtle top glow, soft bottom fade into twilight blue */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#080d19]/20 via-transparent to-[#080d19]" />
        <div className="absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-[#080d19] via-[#080d19]/80 to-transparent" />
      </div>

      {/* Centered Hero Content Matching Velorah Screen */}
      <div className="relative z-10 mx-auto max-w-5xl flex flex-col items-center text-center my-auto">
        {/* Large Editorial Headline with Instrument Serif */}
        <h1 className="font-serif text-5xl sm:text-7xl md:text-8xl font-normal leading-[1.1] tracking-tight text-white max-w-5xl drop-shadow-md">
          Where waste transforms <br />
          <span className="italic font-light text-white/95">
            through computer vision.
          </span>
        </h1>

        {/* Subtitle matching Velorah prose style */}
        <p className="mt-8 max-w-2xl text-base sm:text-lg text-white/85 leading-relaxed font-sans font-light drop-shadow">
          We're designing tools for deep precision, smart recycling, and cleaner ecosystems.
          Amid the chaos, we classify materials for sharp focus and high impact.
        </p>

        {/* Centered Liquid Glass Pill Button */}
        <div className="mt-12 flex flex-col sm:flex-row items-center gap-5">
          <button
            type="button"
            onClick={onStartClick}
            className="velorah-btn-primary cursor-pointer rounded-full px-10 sm:px-14 py-4 text-base sm:text-lg font-normal text-white tracking-wide transition-all hover:scale-105 active:scale-95 shadow-2xl"
          >
            Start Classifying
          </button>
        </div>
      </div>

      {/* Down Scroll Indicator */}
      <div className="relative z-10 flex justify-center pb-4">
        <button
          type="button"
          onClick={onStartClick}
          className="text-white/60 hover:text-[#eaa7a3] transition-colors animate-bounce flex flex-col items-center gap-1 cursor-pointer"
        >
          <span className="text-[11px] font-mono tracking-widest uppercase">Explore Classifier</span>
          <ArrowDown className="h-4 w-4" />
        </button>
      </div>
    </section>
  );
};