import { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { HeroSection } from "./components/HeroSection";
import { WasteClassifier } from "./components/WasteClassifier";
import { CategoriesShowcase } from "./components/CategoriesShowcase";
import { ApiContractModal } from "./components/ApiContractModal";
import { Footer } from "./components/Footer";

export function App() {
  const [isContractModalOpen, setIsContractModalOpen] = useState(false);
  const [isMockMode, setIsMockMode] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);

  // Probe local Flask API server on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch("http://localhost:5000/predict", {
          method: "POST",
          // Empty payload to check reachability
        });
        if (res.status === 400 || res.status === 200) {
          setApiConnected(true);
        } else {
          setApiConnected(false);
        }
      } catch {
        setApiConnected(false);
      }
    };
    checkBackend();
  }, []);

  const scrollToClassifier = () => {
    const el = document.getElementById("classifier");
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#080c14] text-[#e7e4de] flex flex-col items-center selection:bg-[#d4a14a]/30 selection:text-white cyber-grid">
      {/* Floating Navbar */}
      <Navbar
        onOpenContractModal={() => setIsContractModalOpen(true)}
        isMockMode={isMockMode}
        setIsMockMode={setIsMockMode}
        apiConnected={apiConnected}
      />

      {/* Hero Section */}
      <HeroSection onStartClick={scrollToClassifier} />

      {/* Interactive Classifier Section */}
      <main className="w-full max-w-6xl px-4 sm:px-8 z-10 relative -mt-8 sm:-mt-16 pb-12">
        <WasteClassifier
          isMockMode={isMockMode}
          onOpenContractModal={() => setIsContractModalOpen(true)}
          setApiConnected={setApiConnected}
        />
      </main>

      {/* Canonical Categories Taxonomy Showcase */}
      <CategoriesShowcase />

      {/* Technical Contract Inspector Modal */}
      <ApiContractModal
        isOpen={isContractModalOpen}
        onClose={() => setIsContractModalOpen(false)}
      />

      {/* Editorial Footer */}
      <Footer />
    </div>
  );
}

export default App;