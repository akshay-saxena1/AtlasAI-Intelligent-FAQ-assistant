import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Sidebar from '../components/layout/Sidebar';
import ChatConsole from '../components/layout/ChatConsole';
import TelemetryPanel from '../components/layout/TelemetryPanel';
import { Moon, Sun } from 'lucide-react';
import { useTheme, useSession } from '../hooks';
import { type ChatResponse } from '../api/client';

export default function ChatPage({ onAdminClick, isAdmin }: { onAdminClick: () => void; isAdmin: boolean }) {
  const { isDark, toggle } = useTheme();
  const sessionId = useSession();
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);

  return (
    <div className="h-screen flex overflow-hidden" style={{ background: 'var(--bg-primary)' }}>
      {/* Left Sidebar */}
      <Sidebar
        onCategorySelect={setSelectedCategory}
        selectedCategory={selectedCategory}
        sessionId={sessionId}
        onAdminClick={onAdminClick}
        isAdmin={isAdmin}
      />

      {/* Center Console */}
      <main className="flex-1 flex flex-col relative min-w-0">
        {/* Top Bar */}
        <header className="flex items-center justify-between px-6 py-3 border-b" style={{ borderColor: 'var(--border-glass)' }}>
          <div>
            <h1 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
              {selectedCategory || 'All Topics'}
            </h1>
            <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
              Hybrid NLP-powered FAQ search
            </p>
          </div>
          <motion.button
            id="theme-toggle"
            onClick={toggle}
            whileHover={{ scale: 1.1, rotate: 15 }}
            whileTap={{ scale: 0.9 }}
            className="p-2 rounded-xl glass-panel glass-panel-hover"
          >
            {isDark ? <Sun size={16} style={{ color: 'var(--accent-primary)' }} /> : <Moon size={16} style={{ color: 'var(--accent-primary)' }} />}
          </motion.button>
        </header>

        {/* Chat Area */}
        <div className="flex-1 min-h-0">
          <ChatConsole
            sessionId={sessionId}
            selectedCategory={selectedCategory}
            onResponse={setLastResponse}
          />
        </div>
      </main>

      {/* Right Telemetry Panel */}
      <TelemetryPanel lastResponse={lastResponse} />
    </div>
  );
}
