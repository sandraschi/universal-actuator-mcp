import { Award, Inbox as InboxIcon, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { API_BASE } from "@/lib/api";

interface Milestone {
  title: string;
  description: string;
  type?: string;
  timestamp?: string;
}

interface LogEntry {
  id: string;
  timestamp: string;
  level: string;
  kind: string;
  detail: string;
}

const KIND_BADGE: Record<string, string> = {
  info: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  achievement: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
};

export function Inbox() {
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  const fetchInbox = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [msRes, logRes] = await Promise.all([
        fetch(`${API_BASE}/api/milestones?limit=100`),
        fetch(`${API_BASE}/api/logs?limit=50`),
      ]);
      if (!msRes.ok || !logRes.ok)
        throw new Error(`backend ${msRes.status}/${logRes.status}`);
      const ms = (await msRes.json()) as { milestones: Milestone[] };
      const lg = (await logRes.json()) as { entries: LogEntry[] };
      setMilestones([...(ms.milestones ?? [])].reverse());
      setLogs(lg.entries ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "fetch failed");
      setMilestones([]);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchInbox();
  }, [fetchInbox]);

  const q = query.trim().toLowerCase();
  const filteredMilestones = useMemo(
    () =>
      q
        ? milestones.filter((m) =>
            `${m.title} ${m.description}`.toLowerCase().includes(q),
          )
        : milestones,
    [milestones, q],
  );
  const filteredLogs = useMemo(
    () =>
      q
        ? logs.filter((e) => `${e.kind} ${e.detail}`.toLowerCase().includes(q))
        : logs,
    [logs, q],
  );

  return (
    <div data-testid="inbox-page" className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <InboxIcon className="h-6 w-6 text-emerald-400" /> Inbox
          </h2>
          <p className="text-sm text-slate-300">
            Milestones and recent hub activity
          </p>
        </div>
        <Button
          type="button"
          onClick={() => void fetchInbox()}
          variant="outline"
          className="border-slate-700 text-slate-200"
          data-testid="inbox-refresh"
        >
          <RefreshCw className="mr-2 h-4 w-4" /> Refresh
        </Button>
      </div>

      <div data-testid="inbox-search-row" className="flex gap-2">
        <input
          data-testid="inbox-search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Filter milestones and activity..."
          className="w-full max-w-md rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-white placeholder:text-slate-300"
        />
      </div>

      {loading && (
        <div data-testid="inbox-loading" className="text-sm text-slate-300">
          Loading inbox...
        </div>
      )}
      {error !== null && !loading && (
        <div
          data-testid="inbox-error"
          className="rounded-md border border-red-800 bg-red-950/30 p-4 text-sm text-red-300"
        >
          Backend unreachable ({error}). Start it with{" "}
          <span className="font-mono">just serve</span>, then{" "}
          <button
            type="button"
            className="underline"
            onClick={() => void fetchInbox()}
          >
            retry
          </button>
          .
        </div>
      )}

      {!loading && error === null && (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card
            data-testid="inbox-milestones"
            className="border-slate-800 bg-slate-950/50"
          >
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Award className="h-4 w-4 text-emerald-400" /> Milestones (
                {filteredMilestones.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {filteredMilestones.length === 0 ? (
                <p className="text-sm text-slate-300">
                  No milestones yet. Record one with{" "}
                  <span className="font-mono text-sm">
                    universal_milestone(title=..., description=...)
                  </span>
                  .
                </p>
              ) : (
                <ul className="space-y-3">
                  {filteredMilestones.map((m) => (
                    <li
                      key={`${m.timestamp ?? ""}-${m.title}`}
                      className="rounded-md border border-slate-800 p-3"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm font-medium text-white">
                          {m.title}
                        </span>
                        <span
                          className={`rounded border px-1.5 py-0.5 text-sm ${KIND_BADGE[m.type ?? "info"] ?? KIND_BADGE.info}`}
                        >
                          {m.type ?? "info"}
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-slate-300">
                        {m.description}
                      </p>
                      {m.timestamp !== undefined && (
                        <p className="mt-1 font-mono text-sm text-slate-300">
                          {m.timestamp}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          <Card
            data-testid="inbox-activity"
            className="border-slate-800 bg-slate-950/50"
          >
            <CardHeader>
              <CardTitle className="text-white">
                Recent activity ({filteredLogs.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {filteredLogs.length === 0 ? (
                <p className="text-sm text-slate-300">No activity entries.</p>
              ) : (
                <ul className="space-y-2 font-mono text-sm">
                  {filteredLogs.map((e) => (
                    <li
                      key={e.id}
                      className="flex gap-2 rounded border border-slate-800/60 px-2 py-1.5"
                    >
                      <span className="w-16 shrink-0 text-slate-300">
                        {e.level}
                      </span>
                      <span className="w-20 shrink-0 text-slate-300">
                        [{e.kind}]
                      </span>
                      <span className="break-all text-slate-200">
                        {e.detail}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

export default Inbox;
