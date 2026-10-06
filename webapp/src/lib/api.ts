/**
 * Backend origin. "" in dev (the Vite proxy forwards /api, /health, /chat ... to the dev
 * backend). Installer builds set VITE_API_BASE to the operator backend (see native/build.ps1):
 * the Tauri webview has no proxy.
 */
export const API_BASE: string = import.meta.env.VITE_API_BASE ?? "";
