import React, { useState } from 'react';
import { X, Code, Eye, Copy, Download, ShieldCheck, Check } from 'lucide-react';
import { marked } from 'marked';

export default function ArtifactViewer({ artifact, onClose }) {
  const [activeTab, setActiveTab] = useState('preview'); // preview, code
  const [copied, setCopied] = useState(false);

  if (!artifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = artifact.type === 'html' ? 'html' : 'md';
    const blob = new Blob([artifact.content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${artifact.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.${ext}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-1/2 border-l border-lenny-border bg-slate-950 flex flex-col h-[calc(100vh-4rem)] shadow-2xl relative z-20">
      {/* Artifact Header */}
      <div className="h-14 border-b border-lenny-border px-4 flex items-center justify-between bg-slate-900/90">
        <div className="flex items-center space-x-3">
          <div className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30 text-[10px] uppercase tracking-wider font-bold">
            {artifact.type}
          </div>
          <h3 className="text-xs font-bold text-white truncate max-w-xs">{artifact.title}</h3>
        </div>

        {/* View Tabs & Actions */}
        <div className="flex items-center space-x-2">
          {/* Security Badge */}
          <div className="hidden lg:flex items-center space-x-1 px-2.5 py-1 rounded-md bg-emerald-950/60 border border-emerald-800/40 text-[10px] text-emerald-300">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            <span>Sandboxed Iframe</span>
          </div>

          <div className="flex bg-slate-800 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => setActiveTab('preview')}
              className={`px-3 py-1 rounded-md flex items-center space-x-1.5 transition-all ${
                activeTab === 'preview' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Preview</span>
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`px-3 py-1 rounded-md flex items-center space-x-1.5 transition-all ${
                activeTab === 'code' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code className="w-3.5 h-3.5" />
              <span>Code</span>
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Copy Code"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>

          <button
            onClick={handleDownload}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Download File"
          >
            <Download className="w-4 h-4" />
          </button>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Close Viewer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Artifact Content Area */}
      <div className="flex-1 overflow-hidden bg-slate-900/50 p-4">
        {activeTab === 'preview' ? (
          artifact.type === 'html' ? (
            <iframe
              srcDoc={artifact.content}
              title={artifact.title}
              sandbox="allow-scripts"
              className="w-full h-full rounded-xl bg-white border border-slate-700 shadow-inner"
            />
          ) : (
            <div className="w-full h-full overflow-y-auto p-6 rounded-xl bg-slate-900 border border-slate-800 prose prose-invert prose-sm max-w-none">
              <div dangerouslySetInnerHTML={{ __html: marked.parse(artifact.content || '') }} />
            </div>
          )
        ) : (
          <pre className="w-full h-full overflow-auto p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-indigo-300 leading-relaxed">
            <code>{artifact.content}</code>
          </pre>
        )}
      </div>
    </div>
  );
}
