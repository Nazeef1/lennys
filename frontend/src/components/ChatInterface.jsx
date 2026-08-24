import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, BookOpen, ExternalLink, ChevronDown, ChevronUp, Code2, Bot, User } from 'lucide-react';
import { marked } from 'marked';

export default function ChatInterface({
  messages,
  isLoading,
  onSendMessage,
  onOpenArtifact,
  activeProvider
}) {
  const [inputMessage, setInputMessage] = useState('');
  const [openCitationIdx, setOpenCitationIdx] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;
    onSendMessage(inputMessage);
    setInputMessage('');
  };

  const renderMarkdown = (content) => {
    try {
      const rawHtml = marked.parse(content || '');
      return { __html: rawHtml };
    } catch {
      return { __html: content };
    }
  };

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-4rem)] bg-lenny-dark/60">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto py-12">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-xl mb-4">
              <Sparkles className="w-7 h-7 text-white" />
            </div>
            <h2 className="text-lg font-bold text-white mb-2">Welcome to The Lenny Growth Assistant</h2>
            <p className="text-xs text-slate-400 mb-6 leading-relaxed">
              Ask product strategy questions, generate grounded 1,250-word Ship 30 for 30 essays, or request sandboxed interactive HTML artifacts.
            </p>
            <div className="grid grid-cols-2 gap-3 text-left w-full">
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/40 text-xs text-slate-300">
                <span className="font-semibold text-indigo-400 block mb-1">📚 Knowledge Grounding</span>
                Cited directly from Lenny's Podcast and Newsletter dataset.
              </div>
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/40 text-xs text-slate-300">
                <span className="font-semibold text-purple-400 block mb-1">🖥️ Sandboxed Artifacts</span>
                Side-by-side native HTML & Markdown viewer.
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={msg.id || idx}
              className={`flex items-start space-x-3 ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shrink-0 shadow-md">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}

              <div
                className={`max-w-3xl rounded-2xl p-4 shadow-md text-xs leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none'
                    : 'bg-slate-800/90 text-slate-200 border border-slate-700/60 rounded-tl-none space-y-3'
                }`}
              >
                {/* Message Body */}
                <div
                  className="prose prose-invert prose-xs max-w-none space-y-2"
                  dangerouslySetInnerHTML={renderMarkdown(msg.content)}
                />

                {/* Grounded Citations Accordion */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-700/60">
                    <button
                      onClick={() => setOpenCitationIdx(openCitationIdx === idx ? null : idx)}
                      className="flex items-center justify-between w-full text-[11px] font-semibold text-indigo-300 hover:text-indigo-200"
                    >
                      <span className="flex items-center gap-1.5">
                        <BookOpen className="w-3.5 h-3.5" />
                        Grounded Sources ({msg.citations.length} Transcripts Cited)
                      </span>
                      {openCitationIdx === idx ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    {openCitationIdx === idx && (
                      <div className="mt-2 space-y-2 pl-2">
                        {msg.citations.map((c, cIdx) => (
                          <div key={cIdx} className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px]">
                            <div className="flex items-center justify-between font-semibold text-slate-200">
                              <span>{c.guest} — {c.title}</span>
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                                {c.score} match
                              </span>
                            </div>
                            <p className="text-slate-400 mt-1 italic">"{c.excerpt}"</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Generated Artifact Action Banner */}
                {msg.artifact && (
                  <div className="mt-3 p-3 rounded-xl bg-gradient-to-r from-purple-900/40 to-indigo-900/40 border border-purple-500/30 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Code2 className="w-4 h-4 text-purple-400" />
                      <div>
                        <span className="font-semibold text-white block text-xs">{msg.artifact.title}</span>
                        <span className="text-[10px] text-purple-300 uppercase">Interactive {msg.artifact.type} Artifact</span>
                      </div>
                    </div>
                    <button
                      onClick={() => onOpenArtifact(msg.artifact)}
                      className="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-medium text-[11px] flex items-center space-x-1 shadow-md transition-all"
                    >
                      <span>View Artifact</span>
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center shrink-0">
                  <User className="w-4 h-4 text-slate-300" />
                </div>
              )}
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shrink-0 animate-pulse">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-800/80 border border-slate-700 text-xs text-slate-300 flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
              <span>Analyzing transcript corpus with <strong className="capitalize text-indigo-300">{activeProvider}</strong>...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <div className="p-4 border-t border-lenny-border bg-lenny-card/60">
        <form onSubmit={handleSubmit} className="flex items-center space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask a growth question, request a 1,250-word Ship 30 essay, or generate an HTML artifact..."
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputMessage.trim()}
            className="px-4 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-xs flex items-center justify-center shadow-lg shadow-indigo-600/30 transition-all"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
