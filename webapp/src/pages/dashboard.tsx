import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Activity, Server, ShieldCheck, Zap, Bot, HelpCircle, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export function Dashboard() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Federation Overview</h2>
                    <p className="text-slate-400">Universal Gateway status and domain health</p>
                </div>
            </div>

            {/* Mission / Onboarding Card */}
            <Card className="border-primary/20 bg-primary/5 backdrop-blur-xl glass">
                <CardHeader>
                    <div className="flex items-center gap-2 text-primary mb-2">
                        <HelpCircle className="w-5 h-5" />
                        <span className="text-xs font-bold uppercase tracking-widest">Protocol Mission</span>
                    </div>
                    <CardTitle className="text-2xl text-white">What is the Actuator Hub?</CardTitle>
                    <CardDescription className="text-slate-300 text-base max-w-3xl">
                        The Actuator Hub is a **SOTA Federation Gateway**. It serves as the central nervous system for AI Agents,
                        providing a unified interface to discover, secure, and orchestrate tools across dozens of independent domains
                        (Email, Files, IoT, Git, and more).
                    </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-6 md:grid-cols-3">
                    <div className="space-y-2">
                        <h4 className="text-sm font-bold text-white flex items-center gap-2">
                            <Server className="w-4 h-4 text-emerald-400" />
                            Federate
                        </h4>
                        <p className="text-xs text-slate-400">
                            Connect disparate MCP servers into a single toolbus. No more fragmented API keys or isolated silos.
                        </p>
                    </div>
                    <div className="space-y-2">
                        <h4 className="text-sm font-bold text-white flex items-center gap-2">
                            <Zap className="w-4 h-4 text-orange-400" />
                            Orchestrate
                        </h4>
                        <p className="text-xs text-slate-400">
                            Use the <strong>AI Command</strong> tab to run natural language tasks that span multiple repositories and services.
                        </p>
                    </div>
                    <div className="space-y-2">
                        <h4 className="text-sm font-bold text-white flex items-center gap-2">
                            <Bot className="w-4 h-4 text-blue-400" />
                            Empower
                        </h4>
                        <p className="text-xs text-slate-400">
                            Built for developers and researchers who need their AI agents to interact with the real world safely and efficiently.
                        </p>
                    </div>
                    <div className="md:col-span-3 pt-4 border-t border-white/5 flex gap-4">
                        <Button asChild variant="outline" className="border-primary/20 bg-primary/10 text-primary hover:bg-primary hover:text-white">
                            <Link to="/apps" className="flex items-center gap-2">
                                Discover Apps <ArrowRight className="w-4 h-4" />
                            </Link>
                        </Button>
                        <Button asChild variant="ghost" className="text-slate-400 hover:text-white">
                            <Link to="/chat">Try a Command</Link>
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-md glass">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Active Domains
                        </CardTitle>
                        <Server className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">24</div>
                        <p className="text-xs text-slate-400">
                            +12 mapped in catalog
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-md glass">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Gateway Load
                        </CardTitle>
                        <Activity className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">1.8%</div>
                        <p className="text-xs text-slate-400">
                            Optimized routing
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-md glass">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Routing Health
                        </CardTitle>
                        <ShieldCheck className="h-4 w-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">100%</div>
                        <p className="text-xs text-slate-400">
                            Verified provenance
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-md glass">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Avg Latency
                        </CardTitle>
                        <Zap className="h-4 w-4 text-orange-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">8ms</div>
                        <p className="text-xs text-slate-400">
                            Direct local transport
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 border-slate-800 bg-slate-950/50 glass">
                    <CardHeader>
                        <CardTitle className="text-white">Action Throughput</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[200px] flex items-center justify-center border border-dashed border-slate-800 rounded-md bg-slate-900/20">
                            <span className="text-slate-500 text-sm">Real-time action frequency graph</span>
                        </div>
                    </CardContent>
                </Card>
                <Card className="col-span-3 border-slate-800 bg-slate-950/50 glass">
                    <CardHeader>
                        <CardTitle className="text-white">Recent Actions</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <ActionItem
                                domain="email"
                                action="send_report"
                                status="success"
                                time="2s ago"
                            />
                            <ActionItem
                                domain="github"
                                action="create_pr"
                                status="success"
                                time="45s ago"
                            />
                            <ActionItem
                                domain="knowledge"
                                action="adn_knowledge"
                                status="success"
                                time="2m ago"
                            />
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

function ActionItem({ domain, action, status, time }: { domain: string, action: string, status: string, time: string }) {
    return (
        <div className="flex items-center">
            <span className="relative flex h-2 w-2 mr-2">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${status === 'success' ? 'bg-emerald-400' : 'bg-red-400'} opacity-75`}></span>
                <span className={`relative inline-flex rounded-full h-2 w-2 ${status === 'success' ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
            </span>
            <div className="ml-2 space-y-1">
                <p className="text-sm font-medium leading-none text-white">{action}</p>
                <p className="text-xs text-slate-400">{domain.toUpperCase()}</p>
            </div>
            <div className="ml-auto font-mono text-xs text-slate-400">{time}</div>
        </div>
    );
}
