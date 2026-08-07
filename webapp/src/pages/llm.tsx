import React from 'react';
import { Cpu } from 'lucide-react';

export const LocalLLM: React.FC = () => {
    return (
        <div className="p-6 space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2 text-primary">
                    <Cpu className="w-6 h-6" />
                    <h1 className="text-3xl font-bold tracking-tight text-white">Local LLM Stack</h1>
                </div>
                <p className="text-slate-400">
                    RTX 4090 Orchestration and Inference Management
                </p>
            </div>

            <div className="text-center py-20 border border-dashed border-slate-800 rounded-xl bg-black/20">
                <Cpu className="w-16 h-16 mx-auto text-slate-700 mb-4" />
                <h3 className="text-lg font-semibold text-slate-400 mb-2">No LLM Provider Detected</h3>
                <p className="text-sm text-slate-600 max-w-lg mx-auto">
                    Start Ollama or LM Studio to enable GPU metrics, model management, and inference.
                    The LLM stack page will show live GPU telemetry once a provider is detected.
                </p>
            </div>
        </div>
    );
};

export default LocalLLM;
