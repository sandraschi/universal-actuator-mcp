"use client";

import { HelpCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useBackendStatus } from "@/hooks/use-backend-status";

export function Topbar() {
  const navigate = useNavigate();
  const backend = useBackendStatus();
  const dot =
    backend === "up"
      ? "bg-emerald-400"
      : backend === "down"
        ? "bg-red-400"
        : "bg-slate-500";

  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950/50 px-6 backdrop-blur-xl">
      <div className="flex items-center gap-4">
        <h1 className="text-sm font-medium text-slate-300">
          Navigation / <span className="text-slate-100">Control Center</span>
        </h1>
        <span
          data-testid="backend-dot"
          title={
            backend === "up"
              ? "Backend connected"
              : backend === "down"
                ? "Backend down"
                : "Checking backend"
          }
          className={`inline-block h-2 w-2 rounded-full ${dot}`}
        />
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => navigate("/help")}
          className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-800 bg-slate-900/50 text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
          title="Help"
        >
          <HelpCircle className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
