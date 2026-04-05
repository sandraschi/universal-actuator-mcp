import { useState, useCallback } from 'react';

export interface Toast {
    id: string;
    message: string;
    type: 'success' | 'error' | 'info';
    /** Optional fallback URL shown as an "Open" link */
    url?: string;
}

const TYPE_STYLES: Record<Toast['type'], { bg: string; border: string }> = {
    success: { bg: 'rgba(52,211,153,0.15)', border: 'rgba(52,211,153,0.4)' },
    error: { bg: 'rgba(248,113,113,0.15)', border: 'rgba(248,113,113,0.4)' },
    info: { bg: 'rgba(139,92,246,0.15)', border: 'rgba(139,92,246,0.4)' },
};

const TYPE_ICON: Record<Toast['type'], string> = {
    success: '🚀',
    error: '❌',
    info: 'ℹ️',
};

const AUTO_DISMISS_MS = 5000;

// ── Hook ─────────────────────────────────────────────────────────────────────

export function useToasts() {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const push = useCallback((t: Omit<Toast, 'id'>) => {
        const id = `${Date.now()}-${Math.random()}`;
        setToasts(prev => [...prev, { ...t, id }]);
        setTimeout(
            () => setToasts(prev => prev.filter(x => x.id !== id)),
            AUTO_DISMISS_MS,
        );
    }, []);

    const dismiss = useCallback((id: string) => {
        setToasts(prev => prev.filter(x => x.id !== id));
    }, []);

    return { toasts, push, dismiss };
}

// ── Renderer ─────────────────────────────────────────────────────────────────

interface ToastBarProps {
    toasts: Toast[];
    onDismiss?: (id: string) => void;
}

export function ToastBar({ toasts, onDismiss }: ToastBarProps) {
    if (toasts.length === 0) return null;

    return (
        <div className="fixed bottom-6 right-6 flex flex-col gap-2 z-50 pointer-events-none">
            {toasts.map(t => {
                const { bg, border } = TYPE_STYLES[t.type];
                return (
                    <div
                        key={t.id}
                        className="animate-in slide-in-from-right-4 fade-in duration-300 flex items-center gap-3 px-4 py-3 rounded-xl shadow-xl text-sm font-mono pointer-events-auto"
                        style={{ backgroundColor: bg, border: `1px solid ${border}`, backdropFilter: 'blur(12px)' }}
                    >
                        <span>{TYPE_ICON[t.type]}</span>
                        <span className="text-white">{t.message}</span>
                        {t.url && (
                            <a
                                href={t.url}
                                target="_blank"
                                rel="noreferrer"
                                className="ml-1 underline text-violet-400"
                            >
                                Open
                            </a>
                        )}
                        {onDismiss && (
                            <button
                                onClick={() => onDismiss(t.id)}
                                className="ml-2 text-white/50 hover:text-white transition-colors"
                                aria-label="Dismiss"
                            >
                                ×
                            </button>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
