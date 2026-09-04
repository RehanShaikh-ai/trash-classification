import React, { useState } from "react";
import { X, Copy, Check, Terminal, ShieldAlert, Code2, Layers } from "lucide-react";

interface ApiContractModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ApiContractModal: React.FC<ApiContractModalProps> = ({ isOpen, onClose }) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const curlExample = `curl -X POST http://localhost:5000/predict \\
  -H "Content-Type: multipart/form-data" \\
  -F "image=@sample_waste.jpg"`;

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl animate-fade-in">
      <div className="velorah-card rounded-3xl w-full max-w-3xl max-h-[90vh] overflow-y-auto border border-[#eaa7a3]/30 shadow-2xl p-6 sm:p-9 relative">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-6 right-6 p-2.5 rounded-full velorah-pill text-white/80 hover:text-white hover:border-[#eaa7a3]/50 transition-colors cursor-pointer"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-2xl velorah-pill text-[#eaa7a3] border border-[#eaa7a3]/40">
            <Terminal className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-serif text-2xl sm:text-3xl text-white font-normal">
              Technical Interface Contract v1.0.0
            </h3>
            <p className="text-xs font-mono text-white/60">
              REST API & Integration Specification • Project Version 0.1.0
            </p>
          </div>
        </div>

        {/* Contract Summary Sections */}
        <div className="mt-6 space-y-6">
          {/* Section 12: Frozen API Identifiers */}
          <div className="velorah-glass rounded-2xl p-5 border border-white/15">
            <h4 className="text-xs font-mono uppercase text-[#eaa7a3] tracking-wider mb-3 flex items-center gap-1.5">
              <Layers className="h-4 w-4" />
              Section 12: Frozen Public Identifiers
            </h4>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-white/10 text-white/60">
                    <th className="pb-2">Type</th>
                    <th className="pb-2">Identifier</th>
                    <th className="pb-2">Contract Value</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-white/90">
                  <tr>
                    <td className="py-2.5 text-white/60">Endpoint</td>
                    <td className="py-2.5 text-[#eaa7a3]">/predict</td>
                    <td className="py-2.5">POST http://localhost:5000/predict</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 text-white/60">Request field</td>
                    <td className="py-2.5 text-[#eaa7a3]">image</td>
                    <td className="py-2.5">File (multipart/form-data)</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 text-white/60">Response field</td>
                    <td className="py-2.5 text-emerald-300">predicted_class</td>
                    <td className="py-2.5">cardboard, glass, metal, paper, plastic, trash</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 text-white/60">Response field</td>
                    <td className="py-2.5 text-emerald-300">confidence</td>
                    <td className="py-2.5">float (0.0 &lt;= confidence &lt;= 1.0)</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 text-white/60">Error schema</td>
                    <td className="py-2.5 text-rose-300">error.code, error.message</td>
                    <td className="py-2.5">Structured JSON error payload</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* cURL Command Example */}
          <div className="velorah-glass rounded-2xl p-5 border border-white/15">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs font-mono uppercase text-[#eaa7a3] tracking-wider flex items-center gap-1.5">
                <Code2 className="h-4 w-4" />
                cURL CLI Test Command
              </h4>
              <button
                type="button"
                onClick={() => copyToClipboard(curlExample)}
                className="flex items-center gap-1 text-xs font-mono text-white/70 hover:text-white transition-colors cursor-pointer"
              >
                {copied ? <Check className="h-3.5 w-3.5 text-emerald-300" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{copied ? "Copied" : "Copy cURL"}</span>
              </button>
            </div>
            <pre className="p-3.5 rounded-xl bg-black/40 text-xs font-mono text-[#eaa7a3] overflow-x-auto border border-white/5">
              {curlExample}
            </pre>
          </div>

          {/* Error Codes Matrix */}
          <div className="velorah-glass rounded-2xl p-5 border border-white/15">
            <h4 className="text-xs font-mono uppercase text-rose-300 tracking-wider mb-2 flex items-center gap-1.5">
              <ShieldAlert className="h-4 w-4" />
              Section 11: Documented Error Codes
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs font-mono">
              <div className="p-2.5 rounded-xl bg-black/30 border border-white/5">
                <p className="text-rose-300 font-bold">IMAGE_REQUIRED (400)</p>
                <p className="text-white/60 text-[11px] mt-0.5">No image file was provided in form data.</p>
              </div>
              <div className="p-2.5 rounded-xl bg-black/30 border border-white/5">
                <p className="text-rose-300 font-bold">INVALID_IMAGE (400)</p>
                <p className="text-white/60 text-[11px] mt-0.5">The uploaded file is not a valid decodeable image.</p>
              </div>
              <div className="p-2.5 rounded-xl bg-black/30 border border-white/5">
                <p className="text-rose-300 font-bold">UNSUPPORTED_FILE_TYPE (415)</p>
                <p className="text-white/60 text-[11px] mt-0.5">File format not supported (Must be JPG, JPEG, PNG).</p>
              </div>
              <div className="p-2.5 rounded-xl bg-black/30 border border-white/5">
                <p className="text-rose-300 font-bold">INTERNAL_ERROR (500)</p>
                <p className="text-white/60 text-[11px] mt-0.5">Model runtime exception during tensor inference.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="mt-7 pt-5 border-t border-white/10 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="velorah-pill px-6 py-2.5 rounded-full text-white text-xs font-mono transition-colors cursor-pointer"
          >
            Close Contract Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
