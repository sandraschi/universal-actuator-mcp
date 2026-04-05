import * as React from 'react';
import { X } from 'lucide-react';
import { cn } from '@/common/utils';

interface DialogProps {
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
    children?: React.ReactNode;
}

const Dialog = ({ open, onOpenChange, children }: DialogProps) => {
    React.useEffect(() => {
        const handleKey = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onOpenChange?.(false);
        };
        if (open) document.addEventListener('keydown', handleKey);
        return () => document.removeEventListener('keydown', handleKey);
    }, [open, onOpenChange]);

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center" role="dialog" aria-modal="true">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={() => onOpenChange?.(false)}
                aria-hidden="true"
            />
            {children}
        </div>
    );
};

const DialogContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
    ({ className, children, ...props }, ref) => (
        <div
            ref={ref}
            className={cn(
                'relative z-50 w-full rounded-2xl shadow-2xl ring-1 ring-white/10 animate-in fade-in zoom-in-95 duration-200',
                className
            )}
            {...props}
        >
            {children}
        </div>
    )
);
DialogContent.displayName = 'DialogContent';

const DialogHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
    ({ className, ...props }, ref) => (
        <div ref={ref} className={cn('flex flex-col space-y-1.5 p-6', className)} {...props} />
    )
);
DialogHeader.displayName = 'DialogHeader';

const DialogTitle = React.forwardRef<HTMLHeadingElement, React.HTMLAttributes<HTMLHeadingElement>>(
    ({ className, ...props }, ref) => (
        <h2 ref={ref} className={cn('text-lg font-semibold leading-none tracking-tight', className)} {...props} />
    )
);
DialogTitle.displayName = 'DialogTitle';

const DialogDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
    ({ className, ...props }, ref) => (
        <p ref={ref} className={cn('text-sm text-slate-400', className)} {...props} />
    )
);
DialogDescription.displayName = 'DialogDescription';

const DialogClose = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement>>(
    ({ className, onClick, ...props }, ref) => (
        <button
            ref={ref}
            aria-label="Close dialog"
            title="Close dialog"
            className={cn(
                'absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100 transition-opacity focus:outline-none focus:ring-1 focus:ring-slate-600',
                className
            )}
            onClick={onClick}
            {...props}
        >
            <X className="h-4 w-4" />
        </button>
    )
);
DialogClose.displayName = 'DialogClose';

export { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogClose };
