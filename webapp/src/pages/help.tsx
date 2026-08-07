import { HelpCircle, Shield, Zap, BookOpen, Globe, Link as LinkIcon, Command } from 'lucide-react';

export function Help() {
    const categories = [
        {
            title: "Core Mechanics",
            icon: Zap,
            items: [
                "Domain Orchestration: Unified control across multiple MCP service domains.",
                "Federation Hub: Real-time discovery of available actuator services.",
                "Secure Tunneling: Encrypted communication between actuator and targets."
            ]
        },
        {
            title: "Available Domains",
            icon: Globe,
            items: [
                "Files: Advanced FS operations and Git repository management.",
                "Browser: Automated web interactions and content scraping.",
                "System: Host monitoring and process control.",
                "Robotics: Integration with physical and virtual hardware."
            ]
        },
        {
            title: "Advanced Features",
            icon: Command,
            items: [
                "Task Pipelines: Chain multiple domain actions into complex workflows.",
                "Emergency Stop: Instant termination of all active automation tasks.",
                "Audit Logging: Detailed trace of every action performed across the federation."
            ]
        }
    ]

    return (
        <div className="space-y-12 pb-12 overflow-x-hidden animate-in fade-in duration-500">
            <header className="space-y-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-bold tracking-widest uppercase border border-emerald-500/20">
                    <Shield size={12} />
                    <span>SOTA Standard Documentation</span>
                </div>

                <h1 className="text-5xl font-black tracking-tight text-white leading-[1.1]">
                    Universal Actuator <br />
                    <span className="text-emerald-500">Operation Manual</span>
                </h1>
                <p className="text-slate-400 max-w-2xl text-lg">
                    Master the art of cross-domain orchestration. Learn how to leverage the full power
                    of the Universal Actuator federation.
                </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {categories.map((cat) => (
                    <section
                        key={cat.title}
                        className="p-8 rounded-3xl bg-slate-900/50 border border-slate-800 hover:border-emerald-500/30 transition-all group"

                    >
                        <div className="mb-6 p-4 rounded-2xl bg-slate-800 w-fit group-hover:bg-emerald-500/10 transition-colors">
                            <cat.icon className="text-emerald-500" size={32} />
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-6 underline decoration-emerald-500/50 decoration-2 underline-offset-8">
                            {cat.title}
                        </h2>
                        <ul className="space-y-4">
                            {cat.items.map((item, i) => (
                                <li key={i} className="flex gap-4 text-slate-400 leading-relaxed text-sm">
                                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 shrink-0" />
                                    <span>{item}</span>
                                </li>
                            ))}
                        </ul>
                    </section>
                ))}
            </div>

            <div className="p-10 rounded-[2.5rem] bg-gradient-to-tr from-slate-900 via-slate-900 to-emerald-500/10 border border-slate-800 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-12 opacity-5 pointer-events-none">
                    <BookOpen size={200} />
                </div>

                <div className="relative z-10 space-y-8">
                    <div className="flex items-center gap-4">
                        <div className="p-3 rounded-2xl bg-emerald-500 text-slate-950">
                            <HelpCircle size={28} />
                        </div>
                        <h2 className="text-3xl font-bold text-white">Technical Support</h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-12 text-sm leading-relaxed">
                        <div className="space-y-4">
                            <h3 className="text-emerald-400 font-bold uppercase tracking-widest text-xs">Standard Protocols</h3>
                            <p className="text-slate-300">
                                The Universal Actuator follows the <strong>Materialist Optimization Framework</strong>.
                                Every tool call is strictly validated against current system state to ensure deterministic outcomes.
                            </p>
                            <div className="flex items-center gap-2 text-slate-500">
                                <LinkIcon size={16} />
                                <span>Documentation portal — not yet available</span>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <h3 className="text-emerald-400 font-bold uppercase tracking-widest text-xs">Safety Mechanics</h3>
                            <p className="text-slate-300">
                                A non-interactive 'Dead Man Switch' is active for all high-risk operations.
                                If the orchestration heartbeat is lost, all active domain agents immediately enter safe-state.
                            </p>
                            <div className="flex items-center gap-2 text-slate-500">
                                <Shield size={16} />
                                <span>Emergency protocol — not yet available</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
