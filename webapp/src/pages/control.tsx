import React from "react";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Activity,
    HelpCircle,
    Globe,
    AlertCircle
} from "lucide-react";

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
            </div>

            <div className="text-center py-16 border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
                <Globe className="w-12 h-12 mx-auto text-slate-700 mb-4" />
                <h3 className="text-lg font-semibold text-slate-400 mb-2">No Domains Discovered</h3>
                <p className="text-sm text-slate-600 max-w-md mx-auto">
                    Domain data requires a backend connection.
                    Start the backend MCP server to see registered domains, tool registries, and action history.
                </p>
            </div>

            <Tabs defaultValue="guide" className="space-y-4">
                <TabsList className="bg-slate-900/30 border border-slate-800 p-1">
                    <TabsTrigger value="guide" className="data-[state=active]:bg-slate-800 data-[state=active]:text-white">Protocol Guide</TabsTrigger>
                </TabsList>
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
                                    A real-time index of every Capability provided by connected MCP servers.
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
