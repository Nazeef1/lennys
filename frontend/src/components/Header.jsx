import React, { useState, useEffect } from 'react';
import { Sparkles, Cpu, Database, ChevronDown, Check, ShieldCheck, Activity } from 'lucide-react';

export default function Header({ activeProvider, setActiveProvider, healthInfo, refreshHealth }) {
  const [providers, setProviders] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    fetchProviders();
  }, [activeProvider]);

  const fetchProviders = async () => {
    try {
      const res = await fetch('/api/models');
      if (res.ok) {
        const data = await res.json();
        setProviders(data.providers || []);
      }
    } catch (err) {
      console.error('Failed to fetch providers:', err);
    }
  };

  const handleSelectProvider = async (providerId) => {
    try {
      const res = await fetch('/api/models/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: providerId })
      });
      if (res.ok) {
        setActiveProvider(providerId);
        setIsDropdownOpen(false);
        refreshHealth();
      }
    } catch (err) {
      console.error('Failed to select provider:', err);
    }
  };

  return (
    <header className="h-16 border-b border-lenny-border bg-lenny-card/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Brand Title */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-orange-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            The Lenny Growth Assistant
            <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              Forward Deployed AI
            </span>
          </h1>
          <p className="text-xs text-slate-400">Grounded in Lenny's Podcast & Newsletter Knowledge</p>
        </div>
      </div>

      {/* Controls & Badges */}
      <div className="flex items-center space-x-4">
        {/* RAG Knowledge Status Badge */}
        <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/50 text-xs text-slate-300">
          <Database className="w-3.5 h-3.5 text-emerald-400" />
          <span>Index: <strong className="text-white">{healthInfo?.indexed_chunks || 0}</strong> Chunks</span>
        </div>

        {/* Model Selector Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-indigo-950/60 border border-indigo-800/50 text-xs font-medium text-indigo-200 hover:bg-indigo-900/60 transition-all shadow-sm"
          >
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span className="capitalize">{activeProvider || 'ollama'}</span>
            <ChevronDown className="w-3.5 h-3.5 text-indigo-300 ml-1" />
          </button>

          {isDropdownOpen && (
            <div className="absolute right-0 mt-2 w-64 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl z-50 p-1.5 space-y-1">
              <div className="px-3 py-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
                Select Model Provider
              </div>
              {providers.map((p) => (
                <button
                  key={p.id}
                  onClick={() => handleSelectProvider(p.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-xs flex items-center justify-between transition-colors ${
                    p.id === activeProvider
                      ? 'bg-indigo-600/30 text-indigo-200 font-semibold border border-indigo-500/30'
                      : 'hover:bg-slate-800 text-slate-300'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <span className={`w-2 h-2 rounded-full ${p.available ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                    <span className="capitalize">{p.name}</span>
                  </div>
                  {p.id === activeProvider && <Check className="w-4 h-4 text-indigo-400" />}
                </button>
              ))}
              <div className="px-3 py-1.5 text-[10px] text-slate-500 flex items-center gap-1 border-t border-slate-800/80">
                <ShieldCheck className="w-3 h-3 text-indigo-400" />
                <span>Auto-resilience fallback enabled</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
