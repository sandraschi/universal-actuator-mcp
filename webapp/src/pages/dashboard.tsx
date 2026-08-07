import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Activity, Server, Zap, Bot, HelpCircle, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export function Dashboard() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Federation Overview</h2>
                    <p className="text-slate-400">Gateway status and domain health</p>
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
                        The Actuator Hub is a SOTA Federation Gateway — a unified interface to discover,
                        secure, and orchestrate tools across independent domains.
                    </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-6 md:grid-cols-3">
                    <div className="space-y-2">
                        <h4 className="text-sm font-bold text-white flex items-center gap-2">
                            <Server className="w-4 h-4 text-emerald-400" />
                            Federate
                        </h4>
                        <p className="text-xs text-slate-400">
                            Connect disparate MCP servers into a single toolbus.
                        </p>
                    </div>
                    <div className="space-y-2">
                        <h4 className="text-sm font-bold text-white flex items-center gap-2">
                            <Zap className="w-4 h-4 text-orange-400" />
                            Orchestrate
                        </h4>
                        <p className="text-xs text-slate-400">
                            Run natural language tasks that span multiple repositories and services.
                        </p>
                    </div>
                    <div className="space-y-2">
                        <h4 className="text-sm font-bold text-white flex items-center gap-2">
                            <Bot className="w-4 h-4 text-blue-400" />
                            Empower
                        </h4>
                        <p className="text-xs text-slate-400">
                            Built for developers and researchers who need AI agents in the real world.
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

            {/* KPI Cards — awaiting backend connection */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-md glass opacity-60">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Active Domains
                        </CardTitle>
                        <Server className="h-4 w-4 text-slate-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-slate-600">—</div>
                        <p className="text-xs text-slate-600">Waiting for backend</p>
                    </CardContent>
                </Card>
                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-md glass opacity-60">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Gateway Load
                        </CardTitle>
                        <Activity className="h-4 w-4 text-slate-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-slate-600">—</div>
                        <p className="text-xs text-slate-600">Waiting for backend</p>
                    </CardContent>
                </Card>
                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-md glass opacity-60">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Routing Health
                        </CardTitle>
                        <Activity className="h-4 w-4 text-slate-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-slate-600">—</div>
                        <p className="text-xs text-slate-600">Waiting for backend</p>
                    </CardContent>
                </Card>
                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-md glass opacity-60">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Avg Latency
                        </CardTitle>
                        <Zap className="h-4 w-4 text-slate-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-slate-600">—</div>
                        <p className="text-xs text-slate-600">Waiting for backend</p>
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
                            <span className="text-slate-600 text-sm">Graph requires backend connection</span>
                        </div>
                    </CardContent>
                </Card>
                <Card className="col-span-3 border-slate-800 bg-slate-950/50 glass">
                    <CardHeader>
                        <CardTitle className="text-white">Recent Actions</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-center py-8 text-slate-600 text-sm">
                            No recent actions — start the backend to see activity.
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
