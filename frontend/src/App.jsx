import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import ArtifactViewer from './components/ArtifactViewer';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [activeProvider, setActiveProvider] = useState('ollama');
  const [healthInfo, setHealthInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeArtifact, setActiveArtifact] = useState(null);

  useEffect(() => {
    fetchHealth();
    fetchSessions();
  }, []);

  useEffect(() => {
    if (activeSessionId) {
      fetchMessages(activeSessionId);
    }
  }, [activeSessionId]);

  const fetchHealth = async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setHealthInfo(data);
        if (data.active_provider) {
          setActiveProvider(data.active_provider);
        }
      }
    } catch (err) {
      console.error('Failed to fetch health:', err);
    }
  };

  const fetchSessions = async () => {
    try {
      const res = await fetch('/api/sessions');
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
        if (data.length > 0 && !activeSessionId) {
          setActiveSessionId(data[0].id);
        } else if (data.length === 0) {
          createNewSession();
        }
      }
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
    }
  };

  const createNewSession = async () => {
    try {
      const res = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New Growth Session' })
      });
      if (res.ok) {
        const newSession = await res.json();
        setSessions((prev) => [newSession, ...prev]);
        setActiveSessionId(newSession.id);
        setMessages([]);
        setActiveArtifact(null);
      }
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const fetchMessages = async (sessionId) => {
    try {
      const res = await fetch(`/api/sessions/${sessionId}/messages`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data);
      }
    } catch (err) {
      console.error('Failed to fetch messages:', err);
    }
  };

  const handleSendMessage = async (text) => {
    let currentSessionId = activeSessionId;
    if (!currentSessionId) {
      await createNewSession();
      return;
    }

    // Add user message optimistic update
    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId,
          message: text,
          provider: activeProvider
        })
      });

      if (res.ok) {
        const data = await res.json();
        const asstMsg = {
          id: data.message_id,
          role: 'assistant',
          content: data.content,
          citations: data.citations || [],
          artifact: data.artifact,
          created_at: new Date().toISOString()
        };
        setMessages((prev) => [...prev, asstMsg]);
        if (data.artifact) {
          setActiveArtifact(data.artifact);
        }
        fetchSessions(); // refresh session list titles
      } else {
        const errData = await res.json();
        alert(`Chat Error: ${errData.detail || 'Failed to process prompt'}`);
      }
    } catch (err) {
      console.error('Chat API Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-lenny-dark text-slate-100 font-sans">
      <Header
        activeProvider={activeProvider}
        setActiveProvider={setActiveProvider}
        healthInfo={healthInfo}
        refreshHealth={fetchHealth}
      />

      <div className="flex flex-1 overflow-hidden relative">
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={(id) => {
            setActiveSessionId(id);
            setActiveArtifact(null);
          }}
          onCreateSession={createNewSession}
          onSendPresetPrompt={handleSendMessage}
        />

        <ChatInterface
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
          onOpenArtifact={(art) => setActiveArtifact(art)}
          activeProvider={activeProvider}
        />

        {activeArtifact && (
          <ArtifactViewer
            artifact={activeArtifact}
            onClose={() => setActiveArtifact(null)}
          />
        )}
      </div>
    </div>
  );
}
