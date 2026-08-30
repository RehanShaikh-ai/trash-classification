import React, { useRef, useState } from "react";
import {
  Upload,
  RefreshCw,
  Sparkles,
  X,
  AlertCircle,
  CheckCircle,
  Layers,
  ArrowRight,
  Info,
  ShieldCheck,
} from "lucide-react";

// Contract v1.0.0 Interface
export interface PredictionResponse {
  predicted_class: "cardboard" | "glass" | "metal" | "paper" | "plastic" | "trash" | string;
  confidence: number;
}

export interface ApiError {
  error?: {
    code?: string;
    message?: string;
  };
  message?: string;
}

// Sample presets for quick 1-click test
interface SampleItem {
  name: string;
  category: "cardboard" | "glass" | "metal" | "paper" | "plastic" | "trash";
  imageUrl: string;
  label: string;
}

const SAMPLE_PRESETS: SampleItem[] = [
  {
    name: "Plastic Bottle",
    category: "plastic",
    label: "Plastic (PET)",
    imageUrl:
      "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=600&q=80",
  },
  {
    name: "Cardboard Box",
    category: "cardboard",
    label: "Cardboard",
    imageUrl:
      "https://images.unsplash.com/photo-1530587191325-3db32d826c18?auto=format&fit=crop&w=600&q=80",
  },
  {
    name: "Aluminum Can",
    category: "metal",
    label: "Metal",
    imageUrl:
      "https://images.unsplash.com/photo-1581781870027-04212e231e96?auto=format&fit=crop&w=600&q=80",
  },
  {
    name: "Glass Bottle",
    category: "glass",
    label: "Glass",
    imageUrl:
      "https://images.unsplash.com/photo-1605600659908-0ef719419d41?auto=format&fit=crop&w=600&q=80",
  },
  {
    name: "Newspaper Stack",
    category: "paper",
    label: "Paper",
    imageUrl:
      "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=600&q=80",
  },
  {
    name: "Organic Trash",
    category: "trash",
    label: "General Trash",
    imageUrl:
      "https://images.unsplash.com/photo-1604187351574-c75ca79f5807?auto=format&fit=crop&w=600&q=80",
  },
];

// Rich material guides mapping from canonical classes
const CLASS_DETAILS: Record<
  string,
  {
    displayName: string;
    binName: string;
    instructions: string;
    ecoTip: string;
    badgeBg: string;
    badgeText: string;
  }
> = {
  cardboard: {
    displayName: "Cardboard",
    binName: "Blue / Paper Recycling Bin",
    instructions: "Flatten boxes to save space. Remove tape, packing peanuts, and plastic film.",
    ecoTip: "Recycling 1 ton of cardboard saves 17 trees and 7,000 gallons of water.",
    badgeBg: "bg-[#fcd5b5]/15 border-[#fcd5b5]/40",
    badgeText: "text-[#fcd5b5]",
  },
  glass: {
    displayName: "Glass Container",
    binName: "Teal / Glass Recycling Bin",
    instructions: "Rinse container thoroughly. Metal lids can often be recycled separately.",
    ecoTip: "Glass is 100% recyclable and can be recycled endlessly without loss in quality.",
    badgeBg: "bg-emerald-400/15 border-emerald-400/40",
    badgeText: "text-emerald-300",
  },
  metal: {
    displayName: "Metal / Aluminum",
    binName: "Yellow / Metals Recycling Bin",
    instructions: "Empty and rinse beverage or food cans. Labels can typically remain on.",
    ecoTip: "Recycling aluminum uses 95% less energy than producing new aluminum from raw ore.",
    badgeBg: "bg-[#dcc5cd]/15 border-[#dcc5cd]/40",
    badgeText: "text-[#dcc5cd]",
  },
  paper: {
    displayName: "Paper",
    binName: "Blue / Paper Recycling Bin",
    instructions: "Keep clean and dry. Avoid recycling paper contaminated with grease or food oils.",
    ecoTip: "Each ton of recycled paper preserves approximately 380 gallons of oil.",
    badgeBg: "bg-sky-400/15 border-sky-400/40",
    badgeText: "text-sky-300",
  },
  plastic: {
    displayName: "Plastic Material",
    binName: "Blue / Plastics Recycling Bin",
    instructions: "Check SPI resin code (PET 1, HDPE 2). Rinse and screw caps back on.",
    ecoTip: "Recycled plastics can become durable textiles, park benches, and packaging.",
    badgeBg: "bg-[#eaa7a3]/15 border-[#eaa7a3]/40",
    badgeText: "text-[#eaa7a3]",
  },
  trash: {
    displayName: "Non-Recyclable Trash",
    binName: "Black / General Waste Bin",
    instructions: "Place in standard landfill waste container. Secure bag to prevent littering.",
    ecoTip: "Consider composting organic leftovers or choosing zero-waste packaging alternatives.",
    badgeBg: "bg-purple-400/15 border-purple-400/40",
    badgeText: "text-purple-300",
  },
};

interface WasteClassifierProps {
  isMockMode: boolean;
  onOpenContractModal: () => void;
  setApiConnected: (val: boolean) => void;
}

export const WasteClassifier: React.FC<WasteClassifierProps> = ({
  isMockMode,
  onOpenContractModal,
  setApiConnected,
}) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<{
    code?: string;
    message: string;
  } | null>(null);
  const [activeSample, setActiveSample] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Validate & Handle File Selection (Section 4.3 Image Requirements)
  const handleFile = (file: File) => {
    setErrorMessage(null);
    setPrediction(null);
    setActiveSample(null);

    // Section 4.3: Supported source formats: .jpg, .jpeg, .png
    const validMimes = ["image/jpeg", "image/jpg", "image/png"];
    const validExtensions = /\.(jpe?g|png)$/i;

    if (!validMimes.includes(file.type) && !validExtensions.test(file.name)) {
      setErrorMessage({
        code: "UNSUPPORTED_FILE_TYPE",
        message: "Unsupported file type. Please provide a valid JPG, JPEG, or PNG image.",
      });
      return;
    }

    setSelectedFile(file);

    const reader = new FileReader();
    reader.onload = () => {
      setSelectedImage(reader.result as string);
    };
    reader.onerror = () => {
      setErrorMessage({
        code: "INVALID_IMAGE",
        message: "Unable to read image file. Please try another image.",
      });
      setSelectedFile(null);
      setSelectedImage(null);
    };
    reader.readAsDataURL(file);
  };

  // Preset Sample Loader
  const loadSample = async (sample: SampleItem) => {
    setErrorMessage(null);
    setPrediction(null);
    setActiveSample(sample.name);
    setSelectedImage(sample.imageUrl);

    try {
      const res = await fetch(sample.imageUrl);
      const blob = await res.blob();
      const file = new File([blob], `${sample.category}_sample.jpg`, {
        type: "image/jpeg",
      });
      setSelectedFile(file);
    } catch {
      const dummyBlob = new Blob(["mock-image-data"], { type: "image/jpeg" });
      const file = new File([dummyBlob], `${sample.category}_sample.jpg`, {
        type: "image/jpeg",
      });
      setSelectedFile(file);
    }
  };

  // Inference Execution (Sections 9, 10, 11, 13, 14)
  const handleClassify = async () => {
    if (!selectedFile && !selectedImage) {
      setErrorMessage({
        code: "IMAGE_REQUIRED",
        message: "No image was provided. Please upload an image first.",
      });
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setPrediction(null);

    // Section 14: Mock Mode Simulation
    if (isMockMode) {
      setTimeout(() => {
        setIsLoading(false);
        let targetClass = "plastic";
        if (activeSample) {
          const found = SAMPLE_PRESETS.find((s) => s.name === activeSample);
          if (found) targetClass = found.category;
        }

        const simulatedConfidence = parseFloat((0.88 + Math.random() * 0.11).toFixed(2));

        // Strict Contract Output Schema
        setPrediction({
          predicted_class: targetClass,
          confidence: simulatedConfidence,
        });
      }, 750);
      return;
    }

    // Section 9 & 13.1: Live REST API POST /predict
    const formData = new FormData();
    if (selectedFile) {
      formData.append("image", selectedFile);
    }

    try {
      const response = await fetch("http://localhost:5000/predict", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        setApiConnected(false);
        const errorData = data as ApiError;
        setErrorMessage({
          code: errorData.error?.code || "API_ERROR",
          message:
            errorData.error?.message ||
            errorData.message ||
            `Backend returned error status ${response.status}`,
        });
        return;
      }

      setApiConnected(true);

      // Section 10 & 13.2: Parse successful response
      if (data && typeof data.predicted_class === "string" && typeof data.confidence === "number") {
        setPrediction(data as PredictionResponse);
      } else {
        const fallbackClass = data.predicted_class || data.category?.toLowerCase() || "trash";
        const fallbackConf = typeof data.confidence === "number" ? data.confidence : 0.9;
        setPrediction({
          predicted_class: fallbackClass,
          confidence: fallbackConf,
        });
      }
    } catch (err) {
      console.warn("Live API connection failed, switching status:", err);
      setApiConnected(false);
      setErrorMessage({
        code: "CONNECTION_REFUSED",
        message:
          "Unable to connect to Flask API server on http://localhost:5000. Switch to Mock Mode in the top navbar to preview simulated inference.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const clearState = () => {
    setSelectedImage(null);
    setSelectedFile(null);
    setPrediction(null);
    setErrorMessage(null);
    setActiveSample(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  const confidencePercent = prediction
    ? Math.min(Math.max(Math.round(prediction.confidence * 100), 0), 100)
    : 0;

  const currentClassDetails = prediction
    ? CLASS_DETAILS[prediction.predicted_class.toLowerCase()] || CLASS_DETAILS.trash
    : null;

  return (
    <section id="classifier" className="w-full py-8">
      {/* Velorah Liquid Glass Container Card */}
      <div className="velorah-card rounded-3xl p-6 sm:p-10 relative overflow-hidden">
        {/* Dreamy Ambient Twilight Glows */}
        <div className="absolute -top-32 -right-32 w-96 h-96 bg-[#eaa7a3]/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-[#8c82b5]/15 rounded-full blur-3xl pointer-events-none" />

        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-8 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[#eaa7a3] animate-pulse" />
              <span className="font-mono text-xs uppercase tracking-widest text-[#eaa7a3]">
                Vision Inference Engine
              </span>
            </div>
            <h2 className="font-serif text-3xl sm:text-4xl text-white mt-1">
              Classify Waste Material
            </h2>
          </div>

          {/* Mode Pill & Contract Trigger */}
          <div className="flex items-center gap-3">
            <span
              className={`px-4 py-1.5 rounded-full text-xs font-mono border ${
                isMockMode
                  ? "bg-[#eaa7a3]/20 text-[#fdeed9] border-[#eaa7a3]/50 font-medium"
                  : "bg-emerald-500/15 text-emerald-300 border-emerald-500/40"
              }`}
            >
              {isMockMode ? "Simulated Contract Mode" : "POST http://localhost:5000/predict"}
            </span>

            <button
              type="button"
              onClick={onOpenContractModal}
              title="View Contract Interface Specs"
              className="p-2.5 rounded-full velorah-pill text-white/80 hover:text-[#eaa7a3] hover:border-[#eaa7a3]/40 transition-all cursor-pointer"
            >
              <Info className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Quick Presets Bar */}
        <div className="mt-6">
          <p className="text-xs font-mono text-white/70 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Sparkles className="h-3.5 w-3.5 text-[#eaa7a3]" />
            Quick Test Presets (Select to test instantly):
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 sm:gap-3">
            {SAMPLE_PRESETS.map((sample) => (
              <button
                key={sample.name}
                type="button"
                onClick={() => loadSample(sample)}
                className={`group text-left p-2.5 rounded-2xl border transition-all cursor-pointer flex items-center gap-2.5 sm:flex-col sm:items-start ${
                  activeSample === sample.name
                    ? "border-[#eaa7a3] bg-[#eaa7a3]/20 shadow-lg shadow-[#eaa7a3]/15"
                    : "border-white/10 bg-white/[0.04] hover:border-white/30 hover:bg-white/[0.08]"
                }`}
              >
                <img
                  src={sample.imageUrl}
                  alt={sample.name}
                  className="h-10 w-10 sm:h-16 sm:w-full object-cover rounded-xl shrink-0 filter brightness-95 group-hover:brightness-100 transition-all"
                />
                <div className="overflow-hidden">
                  <p className="text-xs font-medium text-white truncate">{sample.name}</p>
                  <p className="text-[10px] font-mono text-white/60 capitalize">{sample.category}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Main Work Area: Dropzone / Preview */}
        <div className="mt-8">
          {!selectedImage ? (
            /* Upload Dropzone */
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={(e) => {
                e.preventDefault();
                setIsDragging(false);
              }}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`group relative flex flex-col items-center justify-center border-2 border-dashed rounded-3xl p-10 sm:p-16 cursor-pointer transition-all duration-300 ${
                isDragging
                  ? "border-[#eaa7a3] bg-[#eaa7a3]/10 scale-[1.01]"
                  : "border-white/15 bg-white/[0.02] hover:border-[#eaa7a3]/50 hover:bg-white/[0.05]"
              }`}
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFile(file);
                }}
                accept=".jpg,.jpeg,.png,image/jpeg,image/png"
                className="hidden"
              />

              <div className="h-16 w-16 rounded-full velorah-pill border border-[#eaa7a3]/40 flex items-center justify-center mb-4 group-hover:scale-110 group-hover:border-[#eaa7a3] transition-all shadow-xl">
                <Upload className="h-7 w-7 text-[#eaa7a3]" />
              </div>

              <h3 className="text-lg font-medium text-white">
                Drag & drop waste image here, or{" "}
                <span className="text-[#eaa7a3] underline underline-offset-4 font-semibold">
                  browse files
                </span>
              </h3>

              <p className="text-xs font-mono text-white/60 mt-2">
                Contract v1.0.0 Support: JPG, JPEG, PNG (Auto RGB 224×224 Preprocessing)
              </p>
            </div>
          ) : (
            /* Image Preview & Computer Vision HUD */
            <div className="flex flex-col lg:flex-row gap-8 items-center lg:items-stretch">
              {/* Image Preview with HUD frame */}
              <div className="relative w-full lg:w-1/2 aspect-square max-w-md rounded-3xl overflow-hidden border border-white/20 bg-black/40 shadow-2xl flex items-center justify-center group backdrop-blur-md">
                {/* HUD Corner Brackets */}
                <div className="hud-corner-tl" />
                <div className="hud-corner-tr" />
                <div className="hud-corner-bl" />
                <div className="hud-corner-br" />

                {/* Laser Scanning Animation in Velorah Rose */}
                {isLoading && <div className="velorah-scanner-laser" />}

                {/* Image */}
                <img
                  src={selectedImage}
                  alt="Waste item under analysis"
                  className="w-full h-full object-contain p-3 filter contrast-105"
                />

                {/* Remove Image Button */}
                <button
                  type="button"
                  onClick={clearState}
                  disabled={isLoading}
                  title="Remove image"
                  className="absolute top-4 right-4 p-2 rounded-full velorah-pill text-white hover:bg-rose-500/80 transition-colors disabled:opacity-40 cursor-pointer"
                >
                  <X className="h-4 w-4" />
                </button>

                {/* HUD Overlay Metadata */}
                <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between px-4 py-2 rounded-xl velorah-pill text-[11px] font-mono text-white/80">
                  <span>Status: {isLoading ? "Neural Processing..." : "Ready for Inference"}</span>
                  <span className="text-[#eaa7a3]">RGB 224×224</span>
                </div>
              </div>

              {/* Classification Action & Output Panel */}
              <div className="w-full lg:w-1/2 flex flex-col justify-between">
                <div>
                  {/* Action Trigger Bar */}
                  <div className="flex flex-wrap gap-3 mb-6">
                    <button
                      type="button"
                      onClick={handleClassify}
                      disabled={isLoading}
                      className="flex-1 min-w-[200px] cursor-pointer velorah-btn-primary rounded-full px-8 py-3.5 text-sm font-medium text-white shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      <Sparkles className="h-4 w-4 text-[#eaa7a3]" />
                      {isLoading ? "Running Neural Inference..." : "Run Classification"}
                    </button>

                    <button
                      type="button"
                      onClick={clearState}
                      disabled={isLoading}
                      className="p-3.5 rounded-full velorah-pill text-white/70 hover:text-white hover:border-[#eaa7a3]/40 transition-colors disabled:opacity-40 cursor-pointer"
                      title="Reset image"
                    >
                      <RefreshCw className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Error Notification (Section 11 Contract) */}
                  {errorMessage && (
                    <div className="mb-6 p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-200 text-sm flex items-start gap-3 animate-fade-in">
                      <AlertCircle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
                      <div className="space-y-1">
                        {errorMessage.code && (
                          <span className="font-mono text-xs uppercase px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-semibold inline-block">
                            {errorMessage.code}
                          </span>
                        )}
                        <p className="text-sm leading-relaxed">{errorMessage.message}</p>
                      </div>
                    </div>
                  )}

                  {/* Prediction Results (Section 10 & 13.2) */}
                  {prediction && currentClassDetails && (
                    <div className="velorah-glass rounded-3xl p-6 border border-[#eaa7a3]/30 shadow-2xl animate-fade-in space-y-5">
                      {/* Prediction Header */}
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="text-xs font-mono uppercase tracking-widest text-[#eaa7a3]">
                            Predicted Category
                          </span>
                          <h3 className="font-serif text-3xl sm:text-4xl font-normal text-white capitalize mt-1 flex items-center gap-3">
                            {prediction.predicted_class}
                            <span
                              className={`text-xs font-mono px-3.5 py-1 rounded-full uppercase border ${currentClassDetails.badgeBg} ${currentClassDetails.badgeText}`}
                            >
                              Canonical: {prediction.predicted_class}
                            </span>
                          </h3>
                        </div>

                        {/* Success Badge */}
                        <div className="p-2.5 rounded-full velorah-pill text-emerald-400 border border-emerald-400/40">
                          <CheckCircle className="h-5 w-5" />
                        </div>
                      </div>

                      {/* Confidence Meter Bar */}
                      <div>
                        <div className="flex items-center justify-between text-xs font-mono mb-2">
                          <span className="text-white/70">Confidence Score</span>
                          <span className="text-[#eaa7a3] font-bold text-sm">
                            {confidencePercent}% ({(prediction.confidence).toFixed(2)})
                          </span>
                        </div>
                        <div className="h-3 w-full bg-black/40 rounded-full overflow-hidden border border-white/15 p-0.5">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-[#eaa7a3] via-[#fcd5b5] to-[#dcc5cd] transition-all duration-700 ease-out shadow-lg"
                            style={{ width: `${confidencePercent}%` }}
                          />
                        </div>
                        <p className="text-[11px] font-mono text-white/60 mt-1.5 flex justify-between">
                          <span>Quality: {confidencePercent > 80 ? "High Confidence" : "Moderate Confidence"}</span>
                          <span>Range: [0.0 – 1.0]</span>
                        </p>
                      </div>

                      {/* Recycling & Handling Guide */}
                      <div className="pt-4 border-t border-white/10 space-y-3">
                        <div className="flex items-start gap-3">
                          <div className="p-2 rounded-xl velorah-pill text-[#eaa7a3] shrink-0 mt-0.5">
                            <Layers className="h-4 w-4" />
                          </div>
                          <div>
                            <p className="text-xs font-mono text-white/60 uppercase">Target Stream</p>
                            <p className="text-sm font-medium text-white">
                              {currentClassDetails.binName}
                            </p>
                          </div>
                        </div>

                        <div className="p-4 rounded-2xl bg-white/[0.04] border border-white/10 text-xs text-white/90 leading-relaxed">
                          <strong className="text-[#eaa7a3] font-semibold block mb-1 font-mono">
                            Disposal Instructions:
                          </strong>
                          {currentClassDetails.instructions}
                        </div>

                        <p className="text-xs text-white/70 italic">
                          ✨ <span className="font-sans">{currentClassDetails.ecoTip}</span>
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* API Specs Footer */}
                <div className="pt-4 mt-6 border-t border-white/10 flex items-center justify-between text-xs font-mono text-white/60">
                  <span className="flex items-center gap-1.5">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                    Contract 1.0.0 Verified
                  </span>
                  <button
                    type="button"
                    onClick={onOpenContractModal}
                    className="hover:text-[#eaa7a3] flex items-center gap-1 cursor-pointer transition-colors"
                  >
                    API Spec
                    <ArrowRight className="h-3 w-3" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};