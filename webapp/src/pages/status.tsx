import React from 'react';
import { Server, Cpu, Activity } from 'lucide-react';

export const Status: React.FC = () => {
  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
            System Status
          </h1>
          <p className="text-white/50 text-sm mt-1">Health telemetry across the federation.</p>
        </div>
      </div>

      <div className="text-center py-20 border border-dashed border-white/10 rounded-xl">
        <Server className="w-12 h-12 mx-auto text-white/20 mb-4" />
        <h3 className="text-lg font-semibold text-white/50 mb-2">No Status Data Available</h3>
        <p className="text-sm text-white/30 max-w-md mx-auto">
          System status requires a running backend connection. Start the backend to see node health, resource usage, and federation integrity.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 opacity-50">
        <div className="p-6 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl">
          <div className="flex items-center gap-3 mb-6">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-semibold text-white/90">Host Resources</h2>
          </div>
          <div className="text-sm text-white/40 text-center py-8">
            Resource monitoring requires backend connection
          </div>
        </div>
        <div className="p-6 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl">
          <div className="flex items-center gap-3 mb-6">
            <Activity className="w-5 h-5 text-emerald-400" />
            <h2 className="text-lg font-semibold text-white/90">Federation Integrity</h2>
          </div>
          <div className="text-sm text-white/40 text-center py-8">
            Integrity data not yet available
          </div>
        </div>
      </div>
    </div>
  );
};

export default Status;
