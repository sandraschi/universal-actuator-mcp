import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Cpu, Zap, Activity, ShieldCheck, Thermometer, Settings } from 'lucide-react';
import { Progress } from "@/components/ui/progress";

export const LocalLLM: React.FC = () => {
    return (
        <div className="p-6 space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2 text-primary">
                    <Cpu className="w-6 h-6" />
                    <h1 className="text-3xl font-bold tracking-tight text-white">Local LLM Stack</h1>
                </div>
                <p className="text-slate-400">
                    RTX 4090 Orchestration and Inference Management (Ollama / FastMCP)
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <MetricCard
                    title="VRAM Usage"
                    value="18.4 / 24 GB"
                    progress={76}
                    icon={Activity}
                    color="text-blue-400"
                />
                <MetricCard
                    title="GPU Temp"
                    value="58°C"
                    progress={65}
                    icon={Thermometer}
                    color="text-orange-400"
                />
                <MetricCard
                    title="Active Model"
                    value="Llama 3.3 70B"
                    progress={100}
                    icon={Zap}
                    color="text-emerald-400"
                    description="4-bit Quantized"
                />
                <MetricCard
                    title="Node Status"
                    value="Ready"
                    progress={100}
                    icon={ShieldCheck}
                    color="text-purple-400"
                />
            </div>

            <div className="grid gap-6 md:grid-cols-3">
                <Card className="col-span-2 border-slate-800 bg-black/40 backdrop-blur-xl">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Settings className="w-5 h-5 text-primary" />
                            Model Management
                        </CardTitle>
                        <CardDescription className="text-slate-400">Manage local inference weights and routing</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <ModelRow name="Llama 3.3 70B" size="42 GB" status="loaded" />
                            <ModelRow name="Qwen 2.5 32B" size="19 GB" status="idle" />
                            <ModelRow name="Gemma 3 27B" size="16 GB" status="idle" />
                            <ModelRow name="Mistral Small 3 24B" size="14 GB" status="idle" />
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-black/40 backdrop-blur-xl">
                    <CardHeader>
                        <CardTitle className="text-white text-sm">GPU Specifications</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex justify-between text-xs py-2 border-b border-white/5">
                            <span className="text-slate-500">Device</span>
                            <span className="text-slate-200">NVIDIA RTX 4090</span>
                        </div>
                        <div className="flex justify-between text-xs py-2 border-b border-white/5">
                            <span className="text-slate-500">Cores</span>
                            <span className="text-slate-200">16384 CUDA</span>
                        </div>
                        <div className="flex justify-between text-xs py-2 border-b border-white/5">
                            <span className="text-slate-500">Memory</span>
                            <span className="text-slate-200">24GB GDDR6X</span>
                        </div>
                        <div className="flex justify-between text-xs py-2">
                            <span className="text-slate-500">Driver</span>
                            <span className="text-slate-200">546.12 SOTA</span>
                        </div>
                        <Button className="w-full mt-4 bg-primary/10 hover:bg-primary text-primary hover:text-white border border-primary/20">
                            Run Diagnostics
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

const MetricCard = ({ title, value, progress, icon: Icon, color, description }: any) => (
    <Card className="border-slate-800 bg-black/40 backdrop-blur-xl transition-all hover:border-primary/30">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</CardTitle>
            <Icon className={`w-4 h-4 ${color}`} />
        </CardHeader>
        <CardContent>
            <div className="text-2xl font-bold text-white mb-2">{value}</div>
            <Progress value={progress} className="h-1 bg-white/5" />
            {description && <p className="text-[10px] text-slate-500 mt-2 italic">{description}</p>}
        </CardContent>
    </Card>
);

const ModelRow = ({ name, size, status }: any) => (
    <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
        <div className="flex items-center gap-3">
            <div className={`w-2 h-2 rounded-full ${status === 'loaded' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`} />
            <div>
                <p className="text-sm font-medium text-slate-200">{name}</p>
                <p className="text-[10px] text-slate-500 uppercase">{size}</p>
            </div>
        </div>
        <div className="flex gap-2">
            <Button variant="ghost" size="sm" className="h-8 text-[10px] uppercase text-slate-400">Specs</Button>
            <Button size="sm" className={`h-8 text-[10px] uppercase ${status === 'loaded' ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20' : 'bg-primary/10 text-primary hover:bg-primary hover:text-white'}`}>
                {status === 'loaded' ? 'Unload' : 'Load Model'}
            </Button>
        </div>
    </div>
);

export default LocalLLM;
