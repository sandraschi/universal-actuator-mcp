import { useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

export type BackendState = "up" | "down" | "checking";

/** Backend status: Tauri `backend-status` event when hosted, HTTP poll fallback. */
export function useBackendStatus(pollMs = 10000): BackendState {
  const [state, setState] = useState<BackendState>("checking");

  useEffect(() => {
    let cancelled = false;
    let unlisten: (() => void) | null = null;

    const checkHttp = async () => {
      try {
        const res = await fetch(`${API_BASE}/health`);
        if (!cancelled) setState(res.ok ? "up" : "down");
      } catch {
        if (!cancelled) setState("down");
      }
    };

    const setupTauri = async () => {
      try {
        const mod = await import("@tauri-apps/api/event").catch(() => null);
        if (mod === null || cancelled) return;
        const stop = (await mod
          .listen<string>("backend-status", (event) => {
            if (cancelled) return;
            setState(event.payload === "ready" ? "up" : "down");
          })
          .catch(() => null)) as (() => void) | null;
        if (stop !== null) unlisten = stop;
      } catch {
        /* Tauri API absent (plain browser) - HTTP poll below covers it. */
      }
    };

    void setupTauri();
    void checkHttp();
    const timer = window.setInterval(() => void checkHttp(), pollMs);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
      if (unlisten !== null) unlisten();
    };
  }, [pollMs]);

  return state;
}
