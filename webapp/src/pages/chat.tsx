import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Terminal, Wifi, WifiOff } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const API_BASE = 'http://localhost:10857';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp?: string;
}

export function Chat() {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: 'Federated Hub established. I am ready for cross-domain command orchestration.',
            timestamp: new Date().toLocaleTimeString(),
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isConnected, setIsConnected] = useState<boolean | null>(null);
    const chatEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Ping backend on mount
    useEffect(() => {
        fetch(`${API_BASE}/health`)
            .then(r => setIsConnected(r.ok))
            .catch(() => setIsConnected(false));
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        const ts = new Date().toLocaleTimeString();

        setMessages(prev => [...prev, { role: 'user', content: userMessage, timestamp: ts }]);
        setInput('');
        setIsLoading(true);

        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage }),
            });
            const data = await res.json();
            const reply = data.status === 'success'
                ? data.response
                : `Error: ${data.response ?? 'Unknown backend error'}`;

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: reply,
                timestamp: new Date().toLocaleTimeString(),
            }]);
            setIsConnected(true);
        } catch {
            setIsConnected(false);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Backend unreachable (port 10857). Start the server: uv run python backend/server.py`,
                timestamp: new Date().toLocaleTimeString(),
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e as unknown as React.FormEvent);
        }
    };

    return (
        <div className="flex h-[calc(100vh-8rem)] flex-col space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">AI Command</h2>
                    <p className="text-slate-400">Federated tool orchestration via NL</p>
                </div>
                <div className="flex items-center gap-2">
                    {isConnected === true && (
                        <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-mono">
                            <Wifi className="h-3 w-3" /> LIVE :10857
                        </span>
                    )}
                    {isConnected === false && (
                        <span className="flex items-center gap-1.5 text-xs text-red-400 font-mono">
                            <WifiOff className="h-3 w-3" /> OFFLINE
                        </span>
                    )}
                </div>
            </div>

            {/* Message thread */}
            <Card className="flex-1 border-slate-800 bg-slate-950/50 flex flex-col overflow-hidden backdrop-blur-xl">
                <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((m, i) => (
                        <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            {m.role === 'assistant' && (
                                <div className="h-8 w-8 shrink-0 rounded-full bg-emerald-900/20 flex items-center justify-center border border-emerald-800">
                                    <Bot className="h-4 w-4 text-emerald-400" />
                                </div>
                            )}

                            <div className={`max-w-[80%] flex flex-col gap-1 ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                                <div className="flex items-center gap-2">
                                    <span className={`text-xs font-medium ${m.role === 'user' ? 'text-slate-300' : 'text-emerald-400'}`}>
                                        {m.role === 'user' ? 'Architect' : 'Federation AI'}
                                    </span>
                                    {m.timestamp && (
                                        <span className="text-[10px] text-slate-600">{m.timestamp}</span>
                                    )}
                                </div>
                                <div className={`p-3 rounded-xl text-sm text-slate-200 whitespace-pre-wrap leading-relaxed ${m.role === 'user'
                                        ? 'bg-slate-800 border border-slate-700 rounded-tr-sm'
                                        : 'bg-emerald-950/20 border border-emerald-900/30 rounded-tl-sm'
                                    }`}>
                                    {m.content}
                                </div>
                            </div>

                            {m.role === 'user' && (
                                <div className="h-8 w-8 shrink-0 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
                                    <User className="h-4 w-4 text-slate-400" />
                                </div>
                            )}
                        </div>
                    ))}

                    {/* Typing indicator */}
                    {isLoading && (
                        <div className="flex gap-3">
                            <div className="h-8 w-8 shrink-0 rounded-full bg-emerald-900/20 flex items-center justify-center border border-emerald-800">
                                <Bot className="h-4 w-4 text-emerald-400" />
                            </div>
                            <div className="bg-emerald-950/20 border border-emerald-900/30 rounded-xl rounded-tl-sm p-3">
                                <span className="flex gap-1 items-center">
                                    {[0, 1, 2].map(i => (
                                        <span
                                            key={i}
                                            className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce"
                                            style={{ animationDelay: `${i * 0.15}s` }}
                                        />
                                    ))}
                                </span>
                            </div>
                        </div>
                    )}

                    <div ref={chatEndRef} />
                </CardContent>

                {/* Input bar */}
                <div className="p-4 border-t border-slate-800 bg-slate-900/30">
                    <form onSubmit={handleSubmit} className="flex gap-2">
                        <div className="relative flex-1">
                            <Terminal className="absolute left-3 top-3 h-4 w-4 text-slate-500" />
                            <input
                                className="w-full bg-slate-950 border border-slate-800 rounded-md pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-all"
                                placeholder="Issue a cross-domain command..."
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                disabled={isLoading}
                            />
                        </div>
                        <Button
                            type="submit"
                            size="icon"
                            disabled={isLoading || !input.trim()}
                            className="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40"
                        >
                            <Send className="h-4 w-4" />
                        </Button>
                    </form>
                </div>
            </Card>
        </div>
    );
}
