import React from 'react';
import { MessageSquare, Plus, Zap, BookOpen, Layers, BarChart2 } from 'lucide-react';

export default function Sidebar({ sessions, activeSessionId, onSelectSession, onCreateSession, onSendPresetPrompt }) {
  const PRESET_PROMPTS = [
    {
      title: "Ship 30 Masterclass Essay",
      desc: "1,250-word grounded essay on Product-Led Growth & Retention Loops",
      icon: BookOpen,
      prompt: "Write a ~1,250 word Ship 30 for 30 essay on B2B Product-Led Growth and Retention Loops grounded in Lenny's transcripts."
    },
    {
      title: "Interactive Growth Dashboard",
      desc: "Generate HTML/CSS interactive conversion funnel artifact",
      icon: BarChart2,
      prompt: "Generate an interactive HTML artifact showing a SaaS Growth Metrics Calculator and Funnel Dashboard."
    },
    {
      title: "Shreyas Doshi's LNO Framework",
      desc: "Leverage, Neutral, and Overhead tasks for PM execution",
      icon: Layers,
      prompt: "Explain Shreyas Doshi's LNO Framework for Product Managers with concrete transcript examples."
    },
    {
      title: "Duolingo Growth Strategy",
      desc: "How gamification and retention experiments drove growth",
      icon: Zap,
      prompt: "How did Duolingo reignite user growth according to Lenny's newsletter and transcript analysis?"
    }
  ];

  return (
    <aside className="w-72 border-r border-lenny-border bg-lenny-card/50 flex flex-col h-[calc(100vh-4rem)]">
      {/* New Session Button */}
      <div className="p-4 border-b border-lenny-border">
        <button
          onClick={onCreateSession}
          className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium text-xs flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/25 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>New Growth Session</span>
        </button>
      </div>

      {/* Preset Action Templates */}
      <div className="p-4 border-b border-lenny-border space-y-2">
        <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Growth Templates</h3>
        <div className="space-y-1.5">
          {PRESET_PROMPTS.map((item, idx) => {
            const Icon = item.icon;
            return (
              <button
                key={idx}
                onClick={() => onSendPresetPrompt(item.prompt)}
                className="w-full text-left p-2.5 rounded-lg bg-slate-800/40 hover:bg-slate-800/80 border border-slate-700/40 transition-all group"
              >
                <div className="flex items-center space-x-2 text-indigo-400 group-hover:text-indigo-300">
                  <Icon className="w-3.5 h-3.5" />
                  <span className="text-xs font-semibold text-slate-200">{item.title}</span>
                </div>
                <p className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">{item.desc}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Session History List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-2 mb-2">History</h3>
        {sessions.length === 0 ? (
          <p className="text-xs text-slate-500 px-2 py-4 italic text-center">No previous sessions</p>
        ) : (
          sessions.map((s) => (
            <button
              key={s.id}
              onClick={() => onSelectSession(s.id)}
              className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center space-x-2.5 transition-all ${
                s.id === activeSessionId
                  ? 'bg-indigo-600/20 border border-indigo-500/40 text-white font-medium'
                  : 'hover:bg-slate-800/50 text-slate-400 hover:text-slate-200'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
              <span className="truncate">{s.title || 'Growth Session'}</span>
            </button>
          ))
        )}
      </div>
    </aside>
  );
}
