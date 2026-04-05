import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Save, RefreshCw, Server, Shield } from "lucide-react";

export function Settings() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Gateway Config</h2>
                <p className="text-slate-400">Federation registry and security parameters</p>
            </div>

            <div className="grid gap-6">
                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Server className="h-4 w-4 text-emerald-500" />
                            Federation Registry
                        </CardTitle>
                        <CardDescription className="text-slate-400">Manage sub-MCP server endpoint configurations</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="rounded-md bg-slate-900/50 p-4 border border-slate-800 font-mono text-xs text-slate-300 h-48 overflow-y-auto">
                            <pre>{JSON.stringify({
                                "servers": {
                                    "browser": { "command": "npx", "args": ["@mcp/puppeteer"] },
                                    "files": { "command": "python", "args": ["-m", "file_ops_mcp"] },
                                    "knowledge": { "command": "node", "args": ["build/index.js"] }
                                }
                            }, null, 2)}</pre>
                        </div>
                        <div className="flex gap-2">
                            <Button variant="outline" className="border-slate-800 text-slate-300 hover:bg-slate-800">
                                <RefreshCw className="mr-2 h-4 w-4" />
                                Reload config.json
                            </Button>
                            <Button className="bg-emerald-600 hover:bg-emerald-700">
                                <Save className="mr-2 h-4 w-4" />
                                Save Changes
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Shield className="h-4 w-4 text-blue-500" />
                            Security & Entropy
                        </CardTitle>
                        <CardDescription className="text-slate-400">System-level guardrails and reductionist limits</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">Action Rate Limit (per domain)</Label>
                            <Input
                                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                                defaultValue="500 actions/min"
                            />
                        </div>
                        <Button variant="outline" className="border-slate-800 text-slate-300 hover:bg-slate-800 w-full">
                            Reset Security Protocol
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
