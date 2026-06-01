import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Target, BarChart3, Zap } from 'lucide-react';
import { type ChatResponse } from '../../api/client';

interface TelemetryPanelProps {
  lastResponse: ChatResponse | null;
}

function ConfidenceGauge({ value, label }: { value: number; label: string }) {
  const percentage = Math.round(value * 100);
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (value * circumference);
  const color = value >= 0.7 ? '#22c55e' : value >= 0.45 ? '#f59e0b' : '#ef4444';

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-24 h-24">
        <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
          <circle cx="50" cy="50" r="40" fill="none" stroke="var(--border-glass)" strokeWidth="6" />
          <motion.circle
            cx="50" cy="50" r="40" fill="none" stroke={color} strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: 'easeOut' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.span
            className="text-lg font-bold"
            style={{ color }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, type: 'spring' }}
          >
            {percentage}%
          </motion.span>
        </div>
      </div>
      <span className="text-[10px] mt-2 font-medium" style={{ color: 'var(--text-muted)' }}>{label}</span>
    </div>
  );
}

function ScoreBar({ label, value, color, delay }: { label: string; value: number; color: string; delay: number }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-[11px] font-medium" style={{ color: 'var(--text-secondary)' }}>{label}</span>
        <span className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>
          {(value * 100).toFixed(1)}%
        </span>
      </div>
      <div className="h-2 rounded-full overflow-hidden" style={{ background: 'var(--border-glass)' }}>
        <motion.div
          className="h-full rounded-full"
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${Math.max(value * 100, 2)}%` }}
          transition={{ duration: 0.8, delay, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}

export default function TelemetryPanel({ lastResponse }: TelemetryPanelProps) {
  return (
    <aside
      id="telemetry-panel"
      className="w-72 h-full glass-panel flex flex-col overflow-y-auto"
      style={{ borderRadius: 0, borderLeft: '1px solid var(--border-glass)' }}
    >
      {/* Header */}
      <div className="p-4 border-b" style={{ borderColor: 'var(--border-glass)' }}>
        <div className="flex items-center gap-2">
          <Activity size={14} style={{ color: 'var(--accent-primary)' }} />
          <h2 className="text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>Live Telemetry</h2>
        </div>
        <p className="text-[10px] mt-0.5" style={{ color: 'var(--text-muted)' }}>Real-time engine analytics</p>
      </div>

      {lastResponse ? (
        <div className="p-4 space-y-6">
          {/* Confidence Gauge */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-center"
          >
            <ConfidenceGauge value={lastResponse.confidence} label="Hybrid Confidence" />
          </motion.div>

          {/* Match Status */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="glass-panel p-3 space-y-2"
          >
            <div className="flex items-center gap-2">
              <Target size={12} style={{ color: lastResponse.match_found ? '#22c55e' : '#ef4444' }} />
              <span className="text-[11px] font-medium" style={{ color: 'var(--text-primary)' }}>
                {lastResponse.match_found ? 'Match Found' : 'Fallback Triggered'}
              </span>
            </div>
            {lastResponse.category && (
              <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
                Category: <span style={{ color: 'var(--accent-primary)' }}>{lastResponse.category}</span>
              </p>
            )}
          </motion.div>

          {/* Score Breakdown */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="space-y-3"
          >
            <div className="flex items-center gap-2">
              <BarChart3 size={12} style={{ color: 'var(--accent-primary)' }} />
              <span className="text-[11px] font-semibold" style={{ color: 'var(--text-primary)' }}>
                Score Breakdown
              </span>
            </div>
            <ScoreBar label="Semantic (0.7×)" value={lastResponse.semantic_score} color="#6366f1" delay={0.4} />
            <ScoreBar label="Lexical (0.3×)" value={lastResponse.lexical_score} color="#8b5cf6" delay={0.5} />
            <ScoreBar label="Final Fusion" value={lastResponse.confidence} color="#22c55e" delay={0.6} />
          </motion.div>

          {/* Runner-up FAQs */}
          {lastResponse.suggestions.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="space-y-2"
            >
              <div className="flex items-center gap-2">
                <Zap size={12} style={{ color: 'var(--accent-primary)' }} />
                <span className="text-[11px] font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Runner-up Matches
                </span>
              </div>
              {lastResponse.suggestions.map((s, i) => (
                <motion.div
                  key={s.faq_id}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 + i * 0.1 }}
                  className="glass-panel p-2.5 space-y-1.5"
                >
                  <p className="text-[11px] leading-tight" style={{ color: 'var(--text-primary)' }}>
                    {s.question.length > 60 ? s.question.slice(0, 60) + '...' : s.question}
                  </p>
                  <div className="flex gap-3">
                    <span className="text-[9px] font-mono" style={{ color: 'var(--text-muted)' }}>
                      Sem: {(s.semantic_score * 100).toFixed(1)}%
                    </span>
                    <span className="text-[9px] font-mono" style={{ color: 'var(--text-muted)' }}>
                      Lex: {(s.lexical_score * 100).toFixed(1)}%
                    </span>
                    <span className="text-[9px] font-mono font-bold" style={{ color: 'var(--accent-primary)' }}>
                      Fused: {(s.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}

          {/* Formula */}
          <div className="glass-panel p-3">
            <p className="text-[9px] font-mono leading-relaxed text-center" style={{ color: 'var(--text-muted)' }}>
              Score = (0.7 × Semantic) + (0.3 × Lexical)
              <br />
              Threshold ≥ 0.45
            </p>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="text-center">
            <Activity size={32} className="mx-auto mb-3 opacity-20" style={{ color: 'var(--text-muted)' }} />
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Awaiting query...</p>
            <p className="text-[10px] mt-1" style={{ color: 'var(--text-muted)' }}>Analytics will appear here</p>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="mt-auto p-3 text-center border-t" style={{ borderColor: 'var(--border-glass)' }}>
        <p className="text-[9px]" style={{ color: 'var(--text-muted)' }}>
          CodeAlpha · Akshay Saxena
        </p>
      </div>
    </aside>
  );
}
