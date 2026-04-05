import React, { useState, useEffect } from 'react';
import {
    Wrench,
    Search,
    Terminal,
    Cpu,
    Shield,
    Zap,
    Info,
    ExternalLink,
    ChevronRight,
    Database,
    Network,
    Box,
    Tool,
    Activity,
    Layers,
    AlertCircle,
    CheckCircle2,
    XCircle,
    X,
    Code
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogClose
} from "@/components/ui/dialog";
import { cn } from '@/common/utils';

interface ToolInfo {
    name: string;
    description: string;
    inputSchema: any;
}

interface ServerInfo {
    name: string;
    description: string;
    status: "online" | "offline" | "starting";
    type: "stdio" | "sse";
    tools: ToolInfo[];
    capabilities: string[];
    version: string;
}

function ToolDrilldown({ server, isOpen, onClose }: { server: ServerInfo | null, isOpen: boolean, onClose: () => void }) {
    if (!server) return null;

    return (
        <Dialog open={isOpen} onOpenChange={(open: boolean) => !open && onClose()}>
            <DialogContent className="max-w-4xl max-h-[85vh] overflow-hidden flex flex-col border-slate-800 bg-slate-950 text-slate-200">
                <DialogHeader className="flex flex-row items-center justify-between pb-4 border-b border-slate-800">
                    <div className="space-y-1">
                        <DialogTitle className="text-2xl font-bold flex items-center gap-2 text-white">
                            <Box className="h-6 w-6 text-emerald-400" />
                            {server.name}
                        </DialogTitle>
                        <DialogDescription className="text-slate-400">
                            {server.description}
                        </DialogDescription>
                    </div>
                </DialogHeader>

                <div className="flex-1 overflow-y-auto py-6 space-y-8 pr-2">
                    {/* Capabilities & Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 backdrop-blur-sm">
                            <div className="text-xs text-slate-500 uppercase tracking-widest mb-1">Status</div>
                            <div className="flex items-center gap-2">
                                {server.status === "online" ? (
                                    <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">ONLINE</Badge>
                                ) : (
                                    <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/20">STARTING</Badge>
                                )}
                            </div>
                        </div>
                        <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 backdrop-blur-sm">
                            <div className="text-xs text-slate-500 uppercase tracking-widest mb-1">Type</div>
                            <div className="text-sm font-mono text-blue-400">{server.type.toUpperCase()} Protocol</div>
                        </div>
                        <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 backdrop-blur-sm">
                            <div className="text-xs text-slate-500 uppercase tracking-widest mb-1">Version</div>
                            <div className="text-sm text-slate-300">{server.version || "1.0.0"}</div>
                        </div>
                    </div>

                    {/* Capabilities Tags */}
                    <div className="space-y-3">
                        <h3 className="text-sm font-medium text-slate-400 flex items-center gap-2">
                            <Layers className="h-4 w-4" /> Capabilities
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {server.capabilities.map(cap => (
                                <Badge key={cap} variant="secondary" className="bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700">
                                    {cap}
                                </Badge>
                            ))}
                        </div>
                    </div>

                    {/* Tools List */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-medium text-slate-400 flex items-center gap-2">
                            <Terminal className="h-4 w-4" /> Tools Portmanteau ({server.tools.length})
                        </h3>
                        <div className="grid grid-cols-1 gap-3">
                            {server.tools.map(tool => (
                                <div key={tool.name} className="group p-4 rounded-xl border border-slate-800 bg-slate-900/30 hover:bg-slate-800/50 transition-all">
                                    <div className="flex items-start justify-between mb-2">
                                        <div className="flex items-center gap-2">
                                            <Code className="h-4 w-4 text-emerald-400" />
                                            <span className="font-mono text-sm font-bold text-slate-100">{tool.name}</span>
                                        </div>
                                        <Button variant="ghost" size="icon" className="h-6 w-6 opacity-0 group-hover:opacity-100 text-slate-500 hover:text-white">
                                            <ExternalLink className="h-3 w-3" />
                                        </Button>
                                    </div>
                                    <p className="text-xs text-slate-400 leading-relaxed mb-4">
                                        {tool.description}
                                    </p>

                                    {/* Argument Schema Mini-View */}
                                    <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800/50">
                                        <div className="text-[10px] text-slate-600 uppercase mb-2">Required Arguments</div>
                                        <div className="flex flex-wrap gap-2">
                                            {tool.inputSchema?.required?.map((req: string) => (
                                                <span key={req} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] border border-emerald-500/20 font-mono">
                                                    {req}
                                                </span>
                                            )) || <span className="text-[10px] text-slate-700 italic">No required arguments</span>}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="pt-4 border-t border-slate-800 flex justify-end">
                    <Button onClick={onClose} variant="secondary" className="bg-slate-800 hover:bg-slate-700 text-white">
                        Close Analysis
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}

export function ToolsPage() {
    const [servers, setServers] = useState<ServerInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedServer, setSelectedServer] = useState<ServerInfo | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState(''); // Re-added for the new search input

    const fetchServers = async () => {
        setLoading(true);
        try {
            // In a real SOTA app, we'd hit the FastAPI backend
            const response = await fetch('http://localhost:10854/servers');
            const data = await response.json();

            // Map the schema to our component state
            const mappedServers = Object.entries(data).map(([name, info]: [string, any]) => ({
                name,
                description: info.description || "No description provided",
                status: info.status || "online",
                type: info.type || "stdio",
                tools: info.tools || [],
                capabilities: info.capabilities || ["tools"],
                version: info.version || "1.0.0"
            }));

            setServers(mappedServers);
        } catch (error) {
            console.error("Failed to fetch MCP servers:", error);
            // Fallback for demo if backend is not responding
            setServers([
                {
                    name: "filesystem-hub",
                    description: "Universal file operations and audit logs",
                    status: "online",
                    type: "stdio",
                    tools: [
                        { name: "read_file", description: "Read complete file contents", inputSchema: { required: ["path"] } },
                        { name: "write_file", description: "Write content to files safely", inputSchema: { required: ["path", "content"] } }
                    ],
                    capabilities: ["resources", "tools"],
                    version: "2.14.5"
                },
                {
                    name: "plex-plus",
                    description: "Premium media management and streaming",
                    status: "online",
                    type: "sse",
                    tools: [
                        { name: "scan_library", description: "Trigger library update", inputSchema: { required: ["section"] } }
                    ],
                    capabilities: ["tools"],
                    version: "1.2.0"
                }
            ]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchServers();
    }, []);

    const handleServerClick = (server: ServerInfo) => {
        setSelectedServer(server);
        setIsModalOpen(true);
    };

    const filteredServers = servers.filter(server =>
        server.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        server.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        server.capabilities.some(cap => cap.toLowerCase().includes(searchQuery.toLowerCase())) ||
        server.tools.some(tool => tool.name.toLowerCase().includes(searchQuery.toLowerCase()))
    );


    return (
        <div className="space-y-6 p-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-white">Tools & Domains</h2>
                    <p className="text-slate-400">Deep discovery of federated MCP capabilities</p>
                </div>
                <div className="flex items-center gap-2">
                    <div className="relative">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
                        <input
                            className="bg-slate-900 border-slate-800 rounded-md pl-9 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500 w-[200px] lg:w-[300px]"
                            placeholder="Filter capabilities..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                    <Button onClick={fetchServers} className="bg-emerald-600 hover:bg-emerald-700">Refresh Fleet</Button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {loading ? (
                    Array(3).fill(0).map((_, i) => (
                        <Card key={i} className="border-slate-800 bg-slate-950/50 animate-pulse">
                            <CardContent className="h-40" />
                        </Card>
                    ))
                ) : (
                    filteredServers.map((server) => (
                        <Card
                            key={server.name}
                            className="group relative border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-all cursor-pointer overflow-hidden backdrop-blur-xl"
                            onClick={() => handleServerClick(server)}
                        >
                            <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium text-slate-200 uppercase tracking-wider">
                                    {server.name}
                                </CardTitle>
                                {server.status === "online" ? (
                                    <div className="flex items-center gap-1.5">
                                        <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                                        <span className="text-[10px] font-bold text-emerald-500">READY</span>
                                    </div>
                                ) : (
                                    <div className="flex items-center gap-1.5">
                                        <div className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" />
                                        <span className="text-[10px] font-bold text-amber-500">STARTING</span>
                                    </div>
                                )}
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <p className="text-xs text-slate-400 line-clamp-2 min-h-[32px]">
                                        {server.description}
                                    </p>

                                    <div className="flex items-center gap-4 text-[10px] text-slate-500 font-mono">
                                        <div className="flex items-center gap-1">
                                            <Terminal className="h-3 w-3" />
                                            <span>{server.tools.length} TOOLS</span>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Cpu className="h-3 w-3" />
                                            <span>{server.type.toUpperCase()}</span>
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between pt-2">
                                        <div className="flex flex-wrap gap-1">
                                            {server.capabilities.slice(0, 2).map((cap) => (
                                                <Badge key={cap} variant="secondary" className="bg-slate-900 text-[9px] text-slate-400 border-slate-800">
                                                    {cap}
                                                </Badge>
                                            ))}
                                        </div>
                                        <ChevronRight className="h-4 w-4 text-slate-600 group-hover:text-emerald-500 transition-colors" />
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))
                )}
            </div>

            <div className="pt-4 border-t border-slate-800">
                <h3 className="text-lg font-semibold text-white mb-4">Domain Analytics</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card className="border-slate-800 bg-slate-950/20">
                        <CardContent className="p-4 flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                                <Box className="h-5 w-5" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-white">{servers.length}</div>
                                <div className="text-[10px] text-slate-500 uppercase">Registered Servers</div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="border-slate-800 bg-slate-950/20">
                        <CardContent className="p-4 flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                                <Terminal className="h-5 w-5" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-white">
                                    {servers.reduce((acc, s) => acc + s.tools.length, 0)}
                                </div>
                                <div className="text-[10px] text-slate-500 uppercase">Available Tools</div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>

            <ToolDrilldown
                server={selectedServer}
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
            />
        </div>
    );
}
