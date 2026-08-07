import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Server, Shield } from "lucide-react";

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
                        <CardDescription className="text-slate-400">Configuration not available — requires backend connection</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="text-center py-12 text-slate-500 text-sm">
                            No configuration data loaded. Start the backend to configure federation settings.
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Shield className="h-4 w-4 text-blue-500" />
                            Security & Entropy
                        </CardTitle>
                        <CardDescription className="text-slate-400">Not yet available — backend API required</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">Action Rate Limit (per domain)</Label>
                            <Input
                                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                                defaultValue="500 actions/min"
                                disabled
                            />
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
