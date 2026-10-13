import { Cpu } from "lucide-react";
import type React from "react";
import { useCallback, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { API_BASE } from "@/lib/api";

const LS_PROVIDER = "llm_provider";
const LS_MODEL = "llm_model";

interface ProviderState {
  detected?: boolean;
  configured?: boolean;
  free?: boolean;
  url?: string;
}

interface ProvidersResponse {
  local: Record<string, ProviderState>;
  cloud: Record<string, ProviderState>;
}

function safeGet(key: string): string {
  try {
    return localStorage.getItem(key) ?? "";
  } catch {
    return "";
  }
}

function safeSet(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* ignore */
  }
}

export const LocalLLM: React.FC = () => {
  const [providers, setProviders] = useState<ProvidersResponse | null>(null);
  const [models, setModels] = useState<string[]>([]);
  const [provider, setProvider] = useState(
    () => safeGet(LS_PROVIDER) || "ollama",
  );
  const [model, setModel] = useState(() => safeGet(LS_MODEL));
  const [loading, setLoading] = useState(true);
  const [testResult, setTestResult] = useState<string | null>(null);

  const fetchProviders = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/llm/providers`);
      if (!res.ok) throw new Error(`backend ${res.status}`);
      const data = (await res.json()) as ProvidersResponse;
      setProviders(data);
      if (safeGet(LS_PROVIDER) === "") {
        const firstLive =
          Object.entries(data.local).find(([, p]) => p.detected)?.[0] ??
          "ollama";
        setProvider(firstLive);
        safeSet(LS_PROVIDER, firstLive);
      }
    } catch {
      setProviders(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchModels = useCallback(async (prov: string) => {
    try {
      if (prov === "ollama") {
        const res = await fetch(`${API_BASE}/api/v1/models`);
        if (!res.ok) throw new Error();
        const data = (await res.json()) as { models: string[] };
        setModels(data.models ?? []);
      } else {
        const res = await fetch(`${API_BASE}/api/llm/discover`);
        if (!res.ok) throw new Error();
        setModels([]);
      }
    } catch {
      setModels([]);
    }
  }, []);

  useEffect(() => {
    void fetchProviders();
  }, [fetchProviders]);

  useEffect(() => {
    void fetchModels(provider);
  }, [provider, fetchModels]);

  useEffect(() => {
    safeSet(LS_PROVIDER, provider);
  }, [provider]);

  useEffect(() => {
    safeSet(LS_MODEL, model);
  }, [model]);

  const testProvider = useCallback(async () => {
    setTestResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/llm/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "ping", provider, model }),
      });
      const data = (await res.json()) as { status?: string };
      setTestResult(data.status === "success" ? "ok" : "error");
    } catch {
      setTestResult("unreachable");
    }
  }, [provider, model]);

  const localEntries =
    providers !== null ? Object.entries(providers.local) : [];
  const cloudEntries =
    providers !== null ? Object.entries(providers.cloud) : [];
  const anyLocal = localEntries.some(([, p]) => p.detected);

  return (
    <div className="p-6 space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-primary">
          <Cpu className="w-6 h-6" />
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Local LLM Stack
          </h1>
        </div>
        <p className="text-sm text-slate-300">
          Auto-detected providers on mount. Local is free; cloud needs
          server-side keys.
        </p>
      </div>

      {loading && (
        <p className="text-sm text-slate-300">Probing providers...</p>
      )}

      {!loading && providers === null && (
        <div className="text-center py-20 border border-dashed border-slate-800 rounded-xl bg-black/20">
          <Cpu className="w-16 h-16 mx-auto text-slate-700 mb-4" />
          <h3 className="text-lg font-semibold text-slate-300 mb-2">
            Backend unreachable
          </h3>
          <p className="text-sm text-slate-300 max-w-lg mx-auto">
            Start it with <span className="font-mono">just serve</span>, then
            refresh.
          </p>
        </div>
      )}

      {!loading && providers !== null && (
        <>
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="border-slate-800 bg-slate-950/50">
              <CardHeader>
                <CardTitle className="text-white">
                  Local providers (free)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {localEntries.map(([name, p]) => (
                  <div
                    key={name}
                    data-testid={`llm-provider-card-${name}`}
                    className="flex items-center justify-between rounded-md border border-slate-800 px-3 py-2"
                  >
                    <span className="text-sm text-slate-200">{name}</span>
                    <span
                      className={`flex items-center gap-1.5 font-mono text-sm ${p.detected ? "text-emerald-400" : "text-slate-300"}`}
                    >
                      <span
                        className={`inline-block h-2 w-2 rounded-full ${p.detected ? "bg-emerald-400" : "bg-slate-600"}`}
                      />
                      {p.detected ? "detected" : "not found"}
                    </span>
                  </div>
                ))}
                {!anyLocal && (
                  <p
                    data-testid="llm-onboarding"
                    className="text-sm text-slate-300"
                  >
                    No local LLM running. Install Ollama, pull a model (e.g.{" "}
                    <span className="font-mono">ollama pull llama3</span>), then
                    refresh this page.
                  </p>
                )}
              </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
              <CardHeader>
                <CardTitle className="text-white">
                  Cloud providers (paid, server keys)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {cloudEntries.map(([name, p]) => (
                  <div
                    key={name}
                    data-testid={`llm-provider-card-${name}`}
                    className="flex items-center justify-between rounded-md border border-slate-800 px-3 py-2"
                  >
                    <span className="text-sm text-slate-200">{name}</span>
                    <span className="font-mono text-sm text-slate-300">
                      {p.configured === true
                        ? "key configured"
                        : "no key (set env on server)"}
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <Card className="border-slate-800 bg-slate-950/50">
            <CardHeader>
              <CardTitle className="text-white">Selection</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap items-center gap-3">
              <label className="text-sm text-slate-300" htmlFor="llm-provider">
                Provider
              </label>
              <select
                id="llm-provider"
                data-testid="llm-provider-select"
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="rounded border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-slate-200"
              >
                {[...localEntries, ...cloudEntries].map(([name]) => (
                  <option key={name} value={name}>
                    {name}
                  </option>
                ))}
              </select>
              <label className="text-sm text-slate-300" htmlFor="llm-model">
                Model
              </label>
              <select
                id="llm-model"
                data-testid="llm-model-select"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="rounded border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-slate-200"
              >
                <option value="">(default)</option>
                {models.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
              <button
                type="button"
                data-testid="llm-test"
                onClick={() => void testProvider()}
                className="rounded border border-slate-700 px-3 py-1 text-sm text-slate-200 hover:bg-slate-800"
              >
                Test
              </button>
              {testResult !== null && (
                <span
                  data-testid="llm-test-result"
                  className="font-mono text-sm text-slate-300"
                >
                  {testResult}
                </span>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default LocalLLM;
