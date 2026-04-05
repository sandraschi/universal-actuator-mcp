import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ExternalLink, Grid, Loader2, CheckCircle2, AlertCircle, Terminal } from 'lucide-react';
import { APPS_CATALOG, AppEntry } from '../common/apps-catalog';

const BACKEND = 'http://localhost:10857';

type LaunchStatus = 'idle' | 'launching' | 'launched' | 'no_script' | 'error';

interface AppState {
    status: LaunchStatus;
    message?: string;
}

export const AppsHub: React.FC = () => {
    const [appStates, setAppStates] = useState<Record<string, AppState>>({});

    const setAppStatus = (id: string, state: AppState) =>
        setAppStates(prev => ({ ...prev, [id]: state }));

    const handleLaunch = async (app: AppEntry) => {
        setAppStatus(app.id, { status: 'launching' });
        try {
            const res = await fetch(`${BACKEND}/launch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ app_id: app.id, url: app.url }),
            });
            const data = await res.json();

            if (data.status === 'launched') {
                setAppStatus(app.id, { status: 'launched', message: data.message });
                // Open the URL after a short delay to let the server start
                setTimeout(() => window.open(app.url, '_blank'), 2500);
            } else if (data.status === 'no_script' || data.status === 'script_missing') {
                // No script: fall back to direct open
                setAppStatus(app.id, { status: 'no_script', message: data.message });
                window.open(app.url, '_blank');
            } else {
                setAppStatus(app.id, { status: 'error', message: data.message });
            }
        } catch {
            // Backend offline: just open the URL directly
            setAppStatus(app.id, { status: 'no_script', message: 'Backend offline — opening URL directly.' });
            window.open(app.url, '_blank');
        }

        // Reset to idle after 5 seconds
        setTimeout(() => setAppStatus(app.id, { status: 'idle' }), 5000);
    };

    const getLaunchLabel = (state: AppState | undefined) => {
        switch (state?.status) {
            case 'launching': return { icon: <Loader2 className="w-4 h-4 ml-2 animate-spin" />, text: 'Starting…' };
            case 'launched': return { icon: <CheckCircle2 className="w-4 h-4 ml-2 text-emerald-400" />, text: 'Launched!' };
            case 'no_script': return { icon: <ExternalLink className="w-4 h-4 ml-2" />, text: 'Opening…' };
            case 'error': return { icon: <AlertCircle className="w-4 h-4 ml-2 text-red-400" />, text: 'Error' };
            default: return { icon: <Terminal className="w-4 h-4 ml-2" />, text: 'Launch App' };
        }
    };

    return (
        <div className="p-6 space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2 text-primary">
                    <Grid className="w-5 h-5" />
                    <h1 className="text-3xl font-bold tracking-tight">Apps Hub</h1>
                </div>
                <p className="text-muted-foreground">
                    Discover and launch SOTA-compliant MCP applications across your local infrastructure.
                    Clicking <strong>Launch App</strong> runs the project's <code>start.ps1</code> and opens the UI.
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {APPS_CATALOG.map((app: AppEntry) => {
                    const state = appStates[app.id];
                    const { icon, text } = getLaunchLabel(state);
                    const isLoading = state?.status === 'launching';

                    return (
                        <Card
                            key={app.id}
                            className="group relative overflow-hidden border-white/10 bg-black/40 backdrop-blur-xl transition-all duration-300 hover:border-primary/50 hover:shadow-[0_0_20px_rgba(var(--primary-rgb),0.1)]"
                        >
                            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

                            <CardHeader>
                                <div className="flex items-start justify-between">
                                    <div className="p-3 rounded-xl bg-primary/10 text-primary group-hover:scale-110 transition-transform duration-300">
                                        <app.icon className="w-6 h-6" />
                                    </div>
                                    <Badge variant="secondary" className="bg-white/5 text-white/70 border-white/10">
                                        :{app.port}
                                    </Badge>
                                </div>
                                <div className="mt-4">
                                    <CardTitle className="text-xl group-hover:text-primary transition-colors duration-300">
                                        {app.label}
                                    </CardTitle>
                                    <CardDescription className="line-clamp-2 mt-1">
                                        {app.description}
                                    </CardDescription>
                                </div>
                            </CardHeader>

                            <CardContent>
                                <div className="flex flex-wrap gap-2 mb-4">
                                    {app.tags.map((tag: string) => (
                                        <Badge key={tag} variant="outline" className="text-[10px] uppercase tracking-wider border-white/5 bg-white/5">
                                            {tag}
                                        </Badge>
                                    ))}
                                </div>

                                {/* Status message */}
                                {state?.message && (
                                    <p className="text-[11px] text-slate-400 mb-3 line-clamp-2">{state.message}</p>
                                )}

                                <div className="flex gap-2">
                                    <Button
                                        className="flex-1 bg-primary/10 hover:bg-primary text-primary hover:text-white border border-primary/20 transition-all duration-300"
                                        onClick={() => handleLaunch(app)}
                                        disabled={isLoading}
                                    >
                                        <span>{text}</span>
                                        {icon}
                                    </Button>
                                    {/* Always allow direct navigation regardless of launch status */}
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        title={`Open ${app.url} directly`}
                                        className="border border-white/10 hover:bg-white/5"
                                        onClick={() => window.open(app.url, '_blank')}
                                    >
                                        <ExternalLink className="w-4 h-4" />
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}

                {/* Placeholder */}
                <Card className="border-dashed border-white/10 bg-transparent flex flex-col items-center justify-center p-8 text-center opacity-50 hover:opacity-100 transition-opacity duration-300">
                    <div className="p-4 rounded-full border border-dashed border-white/20 mb-4">
                        <Grid className="w-8 h-8 text-muted-foreground" />
                    </div>
                    <h3 className="text-lg font-medium">Coming Soon</h3>
                    <p className="text-sm text-muted-foreground mt-2">
                        Automated discovery of newly deployed MCP webapps using the Discovery Service.
                    </p>
                </Card>
            </div>
        </div>
    );
};

