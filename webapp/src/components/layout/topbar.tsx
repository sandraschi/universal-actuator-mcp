'use client';

import { HelpCircle } from 'lucide-react';

export function Topbar() {
    return (
        <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950/50 px-6 backdrop-blur-xl">
            <div className="flex items-center gap-4">
                <h1 className="text-sm font-medium text-slate-400">
                    Navigation / <span className="text-slate-100">Control Center</span>
                </h1>
            </div>

            <div className="flex items-center gap-2">
                {/* System Status Indicator */}
                <div className="mr-4 flex items-center gap-2 rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-500 border border-emerald-500/20">
                    <span className="relative flex h-2 w-2">
                        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
                    </span>
                    System Online
                </div>

                <button
                    className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-800 bg-slate-900/50 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
                    title="Help"
                >
                    <HelpCircle className="h-4 w-4" />
                </button>
            </div>
        </header>
    );
}
