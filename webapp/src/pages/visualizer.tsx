import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Server, Zap, Globe, Cpu, Database, Layout } from "lucide-react";

export function Visualizer() {
    const nodes = [
        { id: "center", x: 400, y: 300, label: "Actuator Hub", icon: Zap, color: "text-emerald-500" },
        { id: "browser", x: 200, y: 150, label: "Browser", icon: Globe, color: "text-blue-500" },
        { id: "files", x: 600, y: 150, label: "Files", icon: Layout, color: "text-purple-500" },
        { id: "knowledge", x: 200, y: 450, label: "Knowledge", icon: Database, color: "text-orange-500" },
        { id: "system", x: 600, y: 450, label: "System", icon: Cpu, color: "text-red-500" },
    ];

    const links = nodes
        .filter(n => n.id !== "center")
        .map(n => ({ source: "center", target: n.id, x1: 400, y1: 300, x2: n.x, y2: n.y }));

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Federation Graph</h2>
                    <p className="text-slate-400">Real-time topology of cross-domain mappings</p>
                </div>
            </div>

            <Card className="border-slate-800 bg-slate-950/50 overflow-hidden backdrop-blur-xl">
                <CardHeader className="border-b border-slate-800/50">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <Server className="h-4 w-4 text-emerald-500" />
                        Domain Topology
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-0 aspect-[16/9] relative bg-slate-900/40">
                    <svg viewBox="0 0 800 600" className="w-full h-full">
                        {/* Links */}
                        {links.map((link, i) => (
                            <line
                                key={i}
                                x1={link.x1}
                                y1={link.y1}
                                x2={link.x2}
                                y2={link.y2}
                                className="stroke-slate-800 stroke-2"
                            />
                        ))}

                        {/* Nodes */}
                        {nodes.map((node) => (
                            <g key={node.id} transform={`translate(${node.x},${node.y})`} className="cursor-pointer group">
                                <circle
                                    r="40"
                                    className={`fill-slate-950 stroke-slate-800 stroke-2 transition-all duration-500 group-hover:stroke-emerald-500 group-hover:r-42 group-hover:shadow-2xl`}
                                />
                                <circle
                                    r="40"
                                    className={`fill-none stroke-emerald-500/20 stroke-1 animate-pulse`}
                                    style={{ animationDuration: '3s' }}
                                />
                                <foreignObject x="-20" y="-20" width="40" height="40">
                                    <div className="w-full h-full flex items-center justify-center">
                                        <node.icon className={`h-6 w-6 ${node.color} transition-transform duration-500 group-hover:scale-110`} />
                                    </div>
                                </foreignObject>
                                <text
                                    y="55"
                                    textAnchor="middle"
                                    className="text-[12px] font-medium fill-slate-300 pointer-events-none transition-colors group-hover:fill-white"
                                >
                                    {node.label}
                                </text>
                            </g>
                        ))}
                    </svg>

                    <div className="absolute top-4 right-4 flex flex-col gap-2">
                        <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-[10px] text-emerald-400 font-mono animate-pulse">
                            LIVE TELEMETRY ACTIVE
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
