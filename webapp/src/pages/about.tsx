import { motion } from 'framer-motion'
import { Info, Bot, Target, Shield, Heart, Github, Star } from 'lucide-react'

export function About() {
    return (
        <div className="space-y-16 max-w-4xl mx-auto py-8">
            <section className="text-center space-y-8">
                <motion.div
                    initial={{ rotate: -10, scale: 0.8, opacity: 0 }}
                    animate={{ rotate: 0, scale: 1, opacity: 1 }}
                    className="relative inline-block"
                >
                    <div className="absolute inset-0 bg-emerald-500 blur-3xl opacity-20 -z-10 animate-pulse" />
                    <div className="p-8 rounded-[3rem] bg-slate-900 border border-emerald-500/20 shadow-2xl shadow-emerald-500/5">
                        <Bot className="w-24 h-24 text-emerald-500" />
                    </div>
                </motion.div>

                <div className="space-y-4">
                    <h1 className="text-6xl font-black text-white tracking-tighter">
                        Universal <span className="text-emerald-500">Actuator</span>
                    </h1>
                    <p className="text-2xl text-slate-400 font-medium">Automated Federation Control v3.4.0</p>
                </div>
            </section>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 px-4">
                <motion.div
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    className="p-10 rounded-3xl bg-slate-900/50 border border-slate-800 space-y-6"
                >
                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                        <Target className="text-emerald-400" />
                        Core Objectives
                    </h2>
                    <p className="text-slate-400 leading-relaxed">
                        Designed as a high-performance substrate for cross-domain tool execution.
                        The Actuator reduces semantic entropy by consolidating specialized domain toolsets
                        into a single, high-availability federation gateway.
                    </p>
                    <ul className="space-y-3 pt-2">
                        {['Zero-latency routing', 'Domain-specific sandboxing', 'Unified audit trails'].map(item => (
                            <li key={item} className="flex items-center gap-3 text-slate-300 text-sm">
                                <Star size={14} className="text-emerald-500" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </motion.div>

                <motion.div
                    initial={{ x: 20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    className="p-10 rounded-3xl bg-slate-900/50 border border-slate-800 space-y-6"
                >
                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                        <Shield className="text-emerald-400" />
                        Security Posture
                    </h2>
                    <p className="text-slate-400 leading-relaxed">
                        Every action is performed under the principle of least privilege.
                        Domain agents are isolated and strictly governed by the federation's
                        central security policy, ensuring complete system integrity.
                    </p>
                    <div className="pt-4 flex items-center gap-4 text-xs font-bold uppercase tracking-[0.2em] text-emerald-500/70">
                        <span>Verified by MCP SOTA</span>
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        <span>2026 Compliant</span>
                    </div>
                </motion.div>
            </div>

            <footer className="pt-16 border-t border-slate-800 flex flex-col items-center gap-8">
                <div className="flex gap-12">
                    <a href="https://github.com/sandraschi/universal-actuator-mcp" target="_blank" rel="noopener noreferrer" className="group flex flex-col items-center gap-3">
                        <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 group-hover:bg-slate-800 transition-colors">
                            <Github className="text-slate-400 group-hover:text-emerald-400" size={24} />
                        </div>
                        <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Source</span>
                    </a>
                    <div className="group flex flex-col items-center gap-3 opacity-40 cursor-not-allowed">
                        <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
                            <Info className="text-slate-400" size={24} />
                        </div>
                        <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Details</span>
                    </div>
                </div>

                <div className="flex items-center gap-3 text-slate-500 text-sm italic">
                    <span>Optimized for performance in Vienna</span>
                    <Heart size={14} className="text-red-500 fill-red-500 animate-pulse" />
                    <span>2026 Actuator Fleet</span>
                </div>
            </footer>
        </div>
    )
}
