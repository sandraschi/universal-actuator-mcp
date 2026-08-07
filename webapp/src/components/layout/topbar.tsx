'use client';

import { HelpCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function Topbar() {
    const navigate = useNavigate();

    return (
        <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950/50 px-6 backdrop-blur-xl">
            <div className="flex items-center gap-4">
                <h1 className="text-sm font-medium text-slate-400">
                    Navigation / <span className="text-slate-100">Control Center</span>
                </h1>
            </div>

            <div className="flex items-center gap-2">
                <button
                    onClick={() => navigate('/help')}
                    className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-800 bg-slate-900/50 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
                    title="Help"
                >
                    <HelpCircle className="h-4 w-4" />
                </button>
            </div>
        </header>
    );
}
