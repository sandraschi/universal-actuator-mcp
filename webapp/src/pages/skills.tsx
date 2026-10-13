import { BookOpen, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { API_BASE } from "@/lib/api";

interface Skill {
  name: string;
  uri: string;
  content: string;
}

export function Skills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSkills = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/skills`);
      if (!res.ok) throw new Error(`backend ${res.status}`);
      const data = (await res.json()) as { skills: Skill[] };
      setSkills(data.skills ?? []);
      setSelected((prev) => prev ?? data.skills?.[0]?.name ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "fetch failed");
      setSkills([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchSkills();
  }, [fetchSkills]);

  const active = skills.find((s) => s.name === selected) ?? null;

  return (
    <div data-testid="skills-page" className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-emerald-400" /> Skills
          </h2>
          <p className="text-sm text-slate-300">
            Domain skills served as MCP resources (skill://)
          </p>
        </div>
        <Button
          type="button"
          onClick={() => void fetchSkills()}
          variant="outline"
          className="border-slate-700 text-slate-200"
          data-testid="skills-refresh"
        >
          <RefreshCw className="mr-2 h-4 w-4" /> Refresh
        </Button>
      </div>

      {loading && (
        <div data-testid="skills-loading" className="text-sm text-slate-300">
          Loading skills...
        </div>
      )}
      {error !== null && !loading && (
        <div
          data-testid="skills-error"
          className="rounded-md border border-red-800 bg-red-950/30 p-4 text-sm text-red-300"
        >
          Backend unreachable ({error}). Start it with{" "}
          <span className="font-mono">just serve</span>, then{" "}
          <button
            type="button"
            className="underline"
            onClick={() => void fetchSkills()}
          >
            retry
          </button>
          .
        </div>
      )}

      {!loading && error === null && (
        <>
          {skills.length === 0 ? (
            <p className="text-sm text-slate-300">No skills registered.</p>
          ) : (
            <div data-testid="skills-list" className="flex flex-wrap gap-2">
              {skills.map((s) => (
                <button
                  key={s.name}
                  type="button"
                  onClick={() => setSelected(s.name)}
                  className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                    selected === s.name
                      ? "border-emerald-500/50 bg-emerald-500/10 text-white"
                      : "border-slate-700 text-slate-300 hover:text-white"
                  }`}
                >
                  {s.name}
                </button>
              ))}
            </div>
          )}
          {active !== null && (
            <Card
              data-testid="skills-viewer"
              className="border-slate-800 bg-slate-950/50"
            >
              <CardHeader>
                <CardTitle className="text-white">{active.name}</CardTitle>
                <p className="font-mono text-sm text-slate-300">{active.uri}</p>
              </CardHeader>
              <CardContent>
                <pre className="max-h-[60vh] overflow-auto whitespace-pre-wrap rounded-md border border-slate-800 bg-black/40 p-4 text-sm text-slate-200">
                  {active.content}
                </pre>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

export default Skills;
