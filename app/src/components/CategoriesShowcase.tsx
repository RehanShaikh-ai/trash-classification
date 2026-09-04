import React from "react";
import {
  Package,
  Wine,
  Sparkles,
  Newspaper,
  Layers,
  Trash2,
  CheckCircle2,
  Clock,
  Recycle,
} from "lucide-react";

interface WasteCategoryInfo {
  id: string;
  name: string;
  icon: React.ReactNode;
  color: string;
  tagColor: string;
  tagBg: string;
  bin: string;
  decompTime: string;
  recyclability: "100% Endlessly Recyclable" | "Highly Recyclable" | "Landfill / Non-Recyclable";
  examples: string[];
  description: string;
}

const CATEGORIES: WasteCategoryInfo[] = [
  {
    id: "cardboard",
    name: "Cardboard",
    icon: <Package className="h-6 w-6 text-[#fcd5b5]" />,
    color: "from-[#fcd5b5]/20 to-transparent",
    tagColor: "text-[#fcd5b5]",
    tagBg: "bg-[#fcd5b5]/15 border-[#fcd5b5]/40",
    bin: "Blue / Paper Stream",
    decompTime: "2 Months",
    recyclability: "Highly Recyclable",
    examples: ["Corrugated boxes", "Cereal packaging", "Shoe boxes", "Cartons"],
    description:
      "Heavy-duty cellulose material. Flattening before binning saves space and improves processing throughput.",
  },
  {
    id: "glass",
    name: "Glass",
    icon: <Wine className="h-6 w-6 text-emerald-300" />,
    color: "from-emerald-400/20 to-transparent",
    tagColor: "text-emerald-300",
    tagBg: "bg-emerald-400/15 border-emerald-400/40",
    bin: "Teal / Glass Stream",
    decompTime: "1,000,000+ Years",
    recyclability: "100% Endlessly Recyclable",
    examples: ["Beverage bottles", "Sauce jars", "Perfumery glass", "Containers"],
    description:
      "Inorganic material melted and reformed indefinitely without loss in purity, strength, or structure.",
  },
  {
    id: "metal",
    name: "Metal",
    icon: <Sparkles className="h-6 w-6 text-[#dcc5cd]" />,
    color: "from-[#dcc5cd]/20 to-transparent",
    tagColor: "text-[#dcc5cd]",
    tagBg: "bg-[#dcc5cd]/15 border-[#dcc5cd]/40",
    bin: "Yellow / Metals Stream",
    decompTime: "50 - 500 Years",
    recyclability: "100% Endlessly Recyclable",
    examples: ["Aluminum cans", "Tin food tins", "Foil wrap", "Aerosol cans"],
    description:
      "Ferrous and non-ferrous metals conserving up to 95% energy in recycling versus primary raw smelting.",
  },
  {
    id: "paper",
    name: "Paper",
    icon: <Newspaper className="h-6 w-6 text-sky-300" />,
    color: "from-sky-400/20 to-transparent",
    tagColor: "text-sky-300",
    tagBg: "bg-sky-400/15 border-sky-400/40",
    bin: "Blue / Paper Stream",
    decompTime: "2 - 6 Weeks",
    recyclability: "Highly Recyclable",
    examples: ["Office sheets", "Magazines", "Envelopes", "Newspapers"],
    description:
      "Pure plant fibers re-pulpable 5 to 7 times. Must remain dry and uncontaminated by oils.",
  },
  {
    id: "plastic",
    name: "Plastic",
    icon: <Layers className="h-6 w-6 text-[#eaa7a3]" />,
    color: "from-[#eaa7a3]/20 to-transparent",
    tagColor: "text-[#eaa7a3]",
    tagBg: "bg-[#eaa7a3]/15 border-[#eaa7a3]/40",
    bin: "Blue / Plastic Stream",
    decompTime: "20 - 500 Years",
    recyclability: "Highly Recyclable",
    examples: ["PET beverage bottles", "HDPE milk jugs", "Cosmetics containers"],
    description:
      "Synthetic polymers indexed under SPI resin codes. Clean rinsing prevents batch contamination.",
  },
  {
    id: "trash",
    name: "Trash",
    icon: <Trash2 className="h-6 w-6 text-purple-300" />,
    color: "from-purple-400/20 to-transparent",
    tagColor: "text-purple-300",
    tagBg: "bg-purple-400/15 border-purple-400/40",
    bin: "Black / General Landfill",
    decompTime: "Variable",
    recyclability: "Landfill / Non-Recyclable",
    examples: ["Soiled packaging", "Sanitary items", "Composite laminates"],
    description:
      "Non-recyclable materials managed safely through municipal waste-to-energy conversion systems.",
  },
];

export const CategoriesShowcase: React.FC = () => {
  return (
    <section id="categories" className="w-full py-20 px-4 sm:px-8 border-t border-white/10">
      <div className="mx-auto max-w-7xl">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-14 gap-6">
          <div>
            <span className="font-mono text-xs text-[#eaa7a3] uppercase tracking-widest flex items-center gap-2">
              <Recycle className="h-3.5 w-3.5" />
              Section 3 Supported Classes
            </span>
            <h2 className="font-serif text-4xl sm:text-5xl text-white mt-2 font-normal">
              Canonical Waste Taxonomy
            </h2>
          </div>
          <p className="max-w-md text-sm text-white/70 leading-relaxed font-light">
            The neural inference pipeline operates strictly against these six canonical classes.
            Contract stability guarantees seamless cross-component integrity.
          </p>
        </div>

        {/* 6 Category Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {CATEGORIES.map((cat) => (
            <div
              key={cat.id}
              className="velorah-card rounded-3xl p-7 hover:border-[#eaa7a3]/50 transition-all duration-500 flex flex-col justify-between group"
            >
              <div>
                {/* Header with Icon & Tag */}
                <div className="flex items-center justify-between mb-5">
                  <div
                    className={`h-12 w-12 rounded-2xl bg-gradient-to-br ${cat.color} velorah-pill flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}
                  >
                    {cat.icon}
                  </div>
                  <span
                    className={`px-3.5 py-1 rounded-full text-xs font-mono font-medium border ${cat.tagBg} ${cat.tagColor}`}
                  >
                    {cat.id}
                  </span>
                </div>

                {/* Name & Description */}
                <h3 className="font-serif text-2xl text-white font-normal mb-2 tracking-wide">{cat.name}</h3>
                <p className="text-xs text-white/70 leading-relaxed mb-5 font-sans font-light">
                  {cat.description}
                </p>

                {/* Common Examples */}
                <div className="space-y-2 mb-6">
                  <p className="text-[11px] font-mono text-[#eaa7a3] uppercase">Sample Items:</p>
                  <div className="flex flex-wrap gap-1.5">
                    {cat.examples.map((ex) => (
                      <span
                        key={ex}
                        className="text-[11px] px-2.5 py-1 rounded-lg velorah-pill text-white/80"
                      >
                        {ex}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Footer Specs */}
              <div className="pt-4 border-t border-white/10 space-y-2 text-xs font-mono text-white/60">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                    Target Stream:
                  </span>
                  <span className="text-white/90">{cat.bin}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Clock className="h-3.5 w-3.5 text-[#eaa7a3]" />
                    Decomp Timeline:
                  </span>
                  <span className="text-white/90">{cat.decompTime}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
