import React from 'react';
import { 
  Activity, 
  Server, 
  Cpu, 
  Database, 
  ShieldCheck, 
  Network, 
  RefreshCcw,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

interface NodeStatusProps {
  name: string;
  status: 'online' | 'degraded' | 'offline';
  uptime: string;
  load: number;
  type: string;
}

const NodeStatusCard: React.FC<NodeStatusProps> = ({ name, status, uptime, load, type }) => {
  const statusColors = {
    online: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5',
    degraded: 'text-amber-400 border-amber-500/20 bg-amber-500/5',
    offline: 'text-rose-400 border-rose-500/20 bg-rose-500/5',
  };

  return (
    <div className={`p-4 rounded-xl border backdrop-blur-md transition-all hover:scale-[1.02] ${statusColors[status]}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="p-2 rounded-lg bg-white/5">
          <Server className="w-5 h-5" />
        </div>
        <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-white/5 text-[10px] font-medium uppercase tracking-wider">
          <span className={`w-1.5 h-1.5 rounded-full ${status === 'online' ? 'bg-emerald-400 animate-pulse' : status === 'degraded' ? 'bg-amber-400' : 'bg-rose-400'}`} />
          {status}
        </div>
      </div>
      <div>
        <h3 className="text-sm font-semibold text-white/90 truncate">{name}</h3>
        <p className="text-xs text-white/50 mb-4 capitalize">{type} Node</p>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-white/40">Load</span>
            <span className="text-white/70 font-mono">{load}%</span>
          </div>
          <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
            <div 
              className={`h-full transition-all duration-500 progress-bar-p${Math.round(load / 5) * 5} ${status === 'online' ? 'bg-emerald-500/50' : status === 'degraded' ? 'bg-amber-500/50' : 'bg-rose-500/50'}`}
            />
          </div>
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-white/40">Uptime</span>
            <span className="text-white/70 font-mono">{uptime}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export const Status: React.FC = () => {
  const nodes: NodeStatusProps[] = [
    { name: 'Universal Hub', status: 'online', uptime: '14d 2h 11m', load: 12, type: 'core' },
    { name: 'Calibre Indexer', status: 'online', uptime: '5d 12h 04m', load: 45, type: 'knowledge' },
    { name: 'Plex Gateway', status: 'online', uptime: '14d 2h 11m', load: 8, type: 'media' },
    { name: 'Immich Bridge', status: 'degraded', uptime: '2d 0h 45m', load: 89, type: 'media' },
    { name: 'DocsOps RAG', status: 'online', uptime: '1h 22m 30s', load: 4, type: 'knowledge' },
    { name: 'Robotics OSC', status: 'offline', uptime: '0s', load: 0, type: 'actuator' },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
            System Status
          </h1>
          <p className="text-white/50 text-sm mt-1">Real-time health telemetry across the federation.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-xs font-medium text-white/70 hover:bg-white/10 transition-colors">
          <RefreshCcw className="w-3.5 h-3.5" />
          Refresh Fleet
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {nodes.map((node) => (
          <NodeStatusCard key={node.name} {...node} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Resource Monitor */}
        <div className="p-6 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl">
          <div className="flex items-center gap-3 mb-6">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-semibold text-white/90">Host Resources</h2>
          </div>
          <div className="space-y-6">
            <div className="space-y-2">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-white/50">CPU Utilization (RTX 4090 Host)</span>
                <span className="text-white/90 font-mono">14%</span>
              </div>
              <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500/50 w-[14%]" />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-white/50">Memory Pressure</span>
                <span className="text-white/90 font-mono">32.4 GB / 64 GB</span>
              </div>
              <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-purple-500/50 w-[51%]" />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-white/50">Network Throughput</span>
                <span className="text-white/90 font-mono">1.2 Gbps</span>
              </div>
              <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-cyan-500/50 w-[72%]" />
              </div>
            </div>
          </div>
        </div>

        {/* Security & Health */}
        <div className="p-6 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl">
          <div className="flex items-center gap-3 mb-6">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h2 className="text-lg font-semibold text-white/90">Federation Integrity</h2>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <p className="text-[10px] text-white/40 uppercase tracking-wider mb-1">Transport</p>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span className="text-sm text-white/80">SSE + Stdio</span>
              </div>
            </div>
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <p className="text-[10px] text-white/40 uppercase tracking-wider mb-1">SSL/TLS</p>
              <div className="flex items-center gap-2 text-rose-400">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">Local Only</span>
              </div>
            </div>
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <p className="text-[10px] text-white/40 uppercase tracking-wider mb-1">LanceDB</p>
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-cyan-400" />
                <span className="text-sm text-white/80">Optimized</span>
              </div>
            </div>
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <p className="text-[10px] text-white/40 uppercase tracking-wider mb-1">Bridge</p>
              <div className="flex items-center gap-2">
                <Network className="w-4 h-4 text-purple-400" />
                <span className="text-sm text-white/80">Connected</span>
              </div>
            </div>
          </div>
          <div className="mt-6 flex items-center gap-2 text-[11px] text-white/30 italic">
            <Activity className="w-3 h-3" />
            Last full sweep: 45 seconds ago
          </div>
        </div>
      </div>
    </div>
  );
};

export default Status;
