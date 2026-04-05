import React from "react";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Zap,
    RefreshCw,
    Terminal,
    Box,
    HelpCircle,
    Activity,
    Shield,
    Database,
    Globe
} from "lucide-react";

interface DomainStatus {
    id: string;
    name: string;
    status: 'active' | 'inactive' | 'error';
    toolCount: number;
    latency: number;
    lastAction: string;
    icon: React.ElementType;
}

const DOMAINS: DomainStatus[] = [
    {
        id: 'browser',
        name: 'Browser Domain',
        status: 'active',
        toolCount: 12,
        latency: 4,
        lastAction: 'navigate(url)',
        icon: Globe
    },
    {
        id: 'files',
        name: 'Files Domain',
        status: 'active',
        toolCount: 8,
        latency: 2,
        lastAction: 'read_file(path)',
        icon: Box
    },
    {
        id: 'knowledge',
        name: 'Knowledge Base',
        status: 'active',
        toolCount: 15,
        latency: 18,
        lastAction: 'adn_knowledge(op)',
        icon: Database
    },
    {
        id: 'system',
        name: 'System Control',
        status: 'active',
        toolCount: 5,
        latency: 1,
        lastAction: 'info()',
        icon: Activity
    }
];

export function Control() {
    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-300 space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-white bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                        Domain Lab
                    </h2>
                    <p className="text-slate-400 mt-1">Federation management and domain orchestration</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" className="border-slate-800 bg-slate-900/40 hover:bg-slate-800 transition-all duration-300">
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Refresh Registry
                    </Button>
                    <Button className="bg-blue-600 hover:bg-blue-500 text-white border-0 shadow-lg shadow-blue-900/20 transition-all duration-300">
                        <Terminal className="mr-2 h-4 w-4" />
                        Manual Probe
                    </Button>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                {DOMAINS.map((domain, index) => (
                    <DomainCard key={domain.id} domain={domain} index={index} />
                ))}
            </div>

            <Tabs defaultValue="actions" className="space-y-4">
                <TabsList className="bg-slate-900/30 border border-slate-800 p-1">
                    <TabsTrigger value="actions" className="data-[state=active]:bg-slate-800 data-[state=active]:text-white">Action History</TabsTrigger>
                    <TabsTrigger value="registry" className="data-[state=active]:bg-slate-800 data-[state=active]:text-white">Tool Registry</TabsTrigger>
                    <TabsTrigger value="mapping" className="data-[state=active]:bg-slate-800 data-[state=active]:text-white">Portmanteau Maps</TabsTrigger>
                    <TabsTrigger value="guide" className="data-[state=active]:bg-slate-800 data-[state=active]:text-white">Protocol Guide</TabsTrigger>
                </TabsList>
                <TabsContent value="actions" className="space-y-4">
                    <HistoryPanel />
                </TabsContent>
                <TabsContent value="registry">
                    <Card className="border-slate-800 bg-slate-950/40 glass">
                        <CardHeader>
                            <CardTitle className="text-white">Global Command Set</CardTitle>
                            <CardDescription className="text-slate-400">Enumerated tools across all federated domains</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="font-mono text-sm space-y-3">
                                <div className="p-3 rounded-lg bg-slate-900/50 border border-white/5">
                                    <span className="text-blue-400 font-bold mr-2">[FILES]</span>
                                    <span className="text-slate-300">read_file, write_file, edit_file, delete_file, list_dir, search_repo</span>
                                </div>
                                <div className="p-3 rounded-lg bg-slate-900/50 border border-white/5">
                                    <span className="text-emerald-400 font-bold mr-2">[BROWSER]</span>
                                    <span className="text-slate-300">navigate, click, type, screenshot, evaluate, wait_for_selector</span>
                                </div>
                                <div className="p-3 rounded-lg bg-slate-900/50 border border-white/5">
                                    <span className="text-purple-400 font-bold mr-2">[SYSTEM]</span>
                                    <span className="text-slate-300">status, help, config, update_env, health_check</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
                <TabsContent value="mapping">
                    <Card className="border-slate-800 bg-slate-950/40 glass">
                        <CardHeader>
                            <CardTitle className="text-white">Portmanteau Maps</CardTitle>
                            <CardDescription className="text-slate-400">Unified tools that abstract complex domain interactions</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid gap-4 md:grid-cols-2">
                                <div className="p-4 rounded-xl bg-gradient-to-br from-blue-500/10 to-transparent border border-blue-500/20">
                                    <h4 className="text-blue-400 font-bold mb-2 flex items-center gap-2">
                                        <Globe className="w-4 h-4" />
                                        adn_research
                                    </h4>
                                    <p className="text-xs text-slate-400 leading-relaxed">
                                        Orchestrates Browser + Search + Knowledge. Automatically synthesizes web findings into semantic memory.
                                    </p>
                                </div>
                                <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-500/10 to-transparent border border-emerald-500/20">
                                    <h4 className="text-emerald-400 font-bold mb-2 flex items-center gap-2">
                                        <Shield className="w-4 h-4" />
                                        adn_system
                                    </h4>
                                    <p className="text-xs text-slate-400 leading-relaxed">
                                        Orchestrates Fleet Monitoring + Config. Core health management across all SOTA endpoints.
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
                <TabsContent value="guide">
                    <Card className="border-blue-500/20 bg-blue-500/5 glow shadow-blue-900/10 glass">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-white">
                                <HelpCircle className="w-5 h-5 text-blue-400" />
                                Gateway Fundamentals
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="grid gap-6 md:grid-cols-2">
                            <div className="space-y-2 border-r border-white/5 pr-6">
                                <h4 className="text-white font-bold text-sm">Federated Tool Registry</h4>
                                <p className="text-xs text-slate-400 leading-relaxed">
                                    A real-time index of every "Capability" provided by connected MCP servers.
                                    The Hub routes requests via standard JSON-RPC 2.0.
                                </p>
                            </div>
                            <div className="space-y-2">
                                <h4 className="text-white font-bold text-sm">Materialist Reduction</h4>
                                <p className="text-xs text-slate-400 leading-relaxed">
                                    Every agentic action is captured, analyzed, and reduced to objective telemetry data
                                    for continuous optimization of the fleet.
                                </p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}

function DomainCard({ domain, index }: { domain: DomainStatus; index: number }) {
    const Icon = domain.icon;
    const loadPct = Math.round((domain.toolCount / 15) * 100);

    return (
        <div
            className="animate-in fade-in slide-in-from-bottom-2 duration-300"
            style={{ animationDelay: `${index * 80}ms`, animationFillMode: 'both' }}
        >
            <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-md group hover:border-slate-700 transition-all duration-300">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-slate-900/80 border border-white/5 text-slate-400 group-hover:text-blue-400 transition-colors">
                            <Icon className="w-4 h-4" />
                        </div>
                        <CardTitle className="text-sm font-medium text-slate-200">
                            {domain.name}
                        </CardTitle>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="mt-4 space-y-4">
                        <div className="flex items-baseline justify-between">
                            <div className="flex flex-col">
                                <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-1">Status</span>
                                <Badge variant="outline" className="border-emerald-500/20 bg-emerald-500/5 text-emerald-400 text-[10px] px-2 py-0">
                                    Online
                                </Badge>
                            </div>
                            <div className="flex flex-col items-end">
                                <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-1">Latency</span>
                                <span className="text-sm font-mono font-bold text-white">{domain.latency}ms</span>
                            </div>
                        </div>

                        <div className="pt-2 border-t border-white/5">
                            <div className="flex justify-between items-center mb-1">
                                <span className="text-[10px] text-slate-500">Registry Load</span>
                                <span className="text-[10px] text-slate-300 font-mono">{domain.toolCount} tools</span>
                            </div>
                            {/* CSS-animated bar replacing framer-motion */}
                            <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-blue-500 rounded-full transition-all duration-1000"
                                    style={{
                                        width: `${loadPct}%`,
                                        transitionDelay: `${500 + index * 80}ms`
                                    }}
                                />
                            </div>
                        </div>

                        <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-white/5">
                            <span className="text-[10px] text-slate-500">Last Op</span>
                            <span className="text-[10px] text-slate-300 font-mono italic">{domain.lastAction}</span>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

function HistoryPanel() {
    const logs = [
        { time: '10:45:12', type: 'ROUTE', domain: 'browser', action: 'navigate', status: 'OKed', details: '242ms', color: 'text-emerald-500' },
        { time: '10:45:15', type: 'ROUTE', domain: 'files', action: 'read_file', status: 'OKed', details: '4ms', color: 'text-emerald-500' },
        { time: '10:45:22', type: 'STATUS', domain: 'knowledge', action: 'ping', status: 'PONG', details: '18ms', color: 'text-blue-500' },
        { time: '10:45:30', type: 'ALERT', domain: 'system', action: 'threshold', status: 'WARN', details: 'load > 0.8', color: 'text-yellow-500' },
        { time: '10:45:45', type: 'AUDIT', domain: 'auth', action: 'session', status: 'VALID', details: 'user_id=102', color: 'text-slate-500' },
        { time: '10:46:02', type: 'ROUTE', domain: 'browser', action: 'screenshot', status: 'STORED', details: 'S3-A12', color: 'text-emerald-500' },
    ];

    return (
        <Card className="border-slate-800 bg-slate-950/40 glass overflow-hidden">
            <CardHeader className="border-b border-white/5">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-white text-sm flex items-center gap-2">
                        <Activity className="w-4 h-4 text-emerald-400 animate-pulse" />
                        Real-time Federation Logs
                    </CardTitle>
                    <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">LIVE</Badge>
                </div>
            </CardHeader>
            <CardContent className="p-0">
                <div className="font-mono text-xs p-4 max-h-[300px] overflow-y-auto space-y-2 scrollbar-thin scrollbar-thumb-slate-800">
                    {logs.map((log, i) => (
                        <div
                            key={i}
                            className="flex items-center gap-2 border-l border-white/5 pl-2 hover:bg-white/5 transition-colors py-1"
                        >
                            <span className="text-slate-600">[{log.time}]</span>
                            <span className={log.color}>{log.type}</span>
                            <span className="text-slate-400">domain={log.domain}</span>
                            <span className="text-slate-200">{log.action}</span>
                            <span className="text-slate-500">(&rarr; {log.status} {log.details})</span>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}

// Silence unused-import lint for Zap (kept for future use)
void Zap;
