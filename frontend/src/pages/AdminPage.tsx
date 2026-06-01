import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area, Legend
} from 'recharts';
import {
  ArrowLeft, Plus, Trash2, Edit3, Save, X, Search, TrendingUp,
  PieChart as PieIcon, BarChart3, Database, CheckCircle, AlertCircle
} from 'lucide-react';
import {
  getDashboardStats, getQueriesOverTime, getCategoryStats,
  getFAQs, getCategories, createFAQ, updateFAQ, deleteFAQ, bulkDeleteFAQs,
  type DashboardStats, type QueryOverTime, type CategoryStats,
  type FAQ, type Category
} from '../api/client';
import { useTheme } from '../hooks';

const CHART_COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#22c55e', '#f59e0b', '#ef4444', '#06b6d4'];

function StatCard({ label, value, icon, color }: { label: string; value: string | number; icon: React.ReactNode; color: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-4 space-y-2"
    >
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-medium" style={{ color: 'var(--text-secondary)' }}>{label}</span>
        <div className="p-1.5 rounded-lg" style={{ background: `${color}20`, color }}>
          {icon}
        </div>
      </div>
      <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{value}</p>
    </motion.div>
  );
}

export default function AdminPage({ onBack }: { onBack: () => void }) {
  const { isDark } = useTheme();
  const [tab, setTab] = useState<'analytics' | 'manage'>('analytics');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [queryData, setQueryData] = useState<QueryOverTime[]>([]);
  const [catStats, setCatStats] = useState<CategoryStats[]>([]);
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editData, setEditData] = useState<{ question: string; answer: string; category_id: number }>({ question: '', answer: '', category_id: 1 });
  const [showCreate, setShowCreate] = useState(false);
  const [newFaq, setNewFaq] = useState({ question: '', answer: '', category_id: 1 });

  const loadAnalytics = useCallback(async () => {
    try {
      const [s, q, c] = await Promise.all([getDashboardStats(), getQueriesOverTime(30), getCategoryStats()]);
      setStats(s);
      setQueryData(q);
      setCatStats(c);
    } catch { /* silent */ }
  }, []);

  const loadFaqs = useCallback(async () => {
    try {
      const [f, c] = await Promise.all([getFAQs(undefined, searchQuery || undefined), getCategories()]);
      setFaqs(f);
      setCategories(c);
    } catch { /* silent */ }
  }, [searchQuery]);

  useEffect(() => { loadAnalytics(); loadFaqs(); }, [loadAnalytics, loadFaqs]);

  const handleDelete = async (id: number) => {
    await deleteFAQ(id);
    loadFaqs();
  };

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    await bulkDeleteFAQs(Array.from(selectedIds));
    setSelectedIds(new Set());
    loadFaqs();
  };

  const handleSaveEdit = async () => {
    if (!editingId) return;
    await updateFAQ(editingId, editData);
    setEditingId(null);
    loadFaqs();
  };

  const handleCreate = async () => {
    if (!newFaq.question || !newFaq.answer) return;
    await createFAQ(newFaq);
    setShowCreate(false);
    setNewFaq({ question: '', answer: '', category_id: 1 });
    loadFaqs();
  };

  const toggleSelect = (id: number) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const textColor = isDark ? '#e8e8f0' : '#1a1a2e';
  const mutedColor = isDark ? '#6a6a80' : '#8888a0';

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ background: 'var(--bg-primary)' }}>
      {/* Header */}
      <header className="flex items-center gap-4 px-6 py-3 border-b" style={{ borderColor: 'var(--border-glass)' }}>
        <motion.button onClick={onBack} whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} className="p-2 rounded-xl glass-panel">
          <ArrowLeft size={16} style={{ color: 'var(--text-primary)' }} />
        </motion.button>
        <div>
          <h1 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Admin Dashboard</h1>
          <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Analytics & FAQ Management · Akshay Saxena</p>
        </div>
        <div className="flex-1" />
        <div className="flex gap-1">
          {(['analytics', 'manage'] as const).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className="px-4 py-1.5 rounded-lg text-xs font-medium transition-all"
              style={{
                background: tab === t ? 'var(--accent-primary)' : 'transparent',
                color: tab === t ? 'white' : 'var(--text-secondary)',
              }}
            >
              {t === 'analytics' ? 'Analytics' : 'Manage FAQs'}
            </button>
          ))}
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {tab === 'analytics' && stats && (
          <div className="space-y-6 max-w-6xl mx-auto">
            {/* Stat Cards */}
            <div className="grid grid-cols-4 gap-4">
              <StatCard label="Total Queries" value={stats.total_queries} icon={<TrendingUp size={14} />} color="#6366f1" />
              <StatCard label="Success Rate" value={`${stats.success_rate}%`} icon={<CheckCircle size={14} />} color="#22c55e" />
              <StatCard label="Total FAQs" value={stats.total_faqs} icon={<Database size={14} />} color="#8b5cf6" />
              <StatCard label="Avg Confidence" value={`${(stats.avg_confidence * 100).toFixed(1)}%`} icon={<BarChart3 size={14} />} color="#f59e0b" />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-2 gap-4">
              {/* Queries Over Time */}
              <div className="glass-panel p-4">
                <h3 className="text-xs font-semibold mb-4 flex items-center gap-2" style={{ color: textColor }}>
                  <TrendingUp size={14} style={{ color: 'var(--accent-primary)' }} />
                  Queries Over Time
                </h3>
                <ResponsiveContainer width="100%" height={220}>
                  <AreaChart data={queryData}>
                    <defs>
                      <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#1a1a2e' : '#e0e0f0'} />
                    <XAxis dataKey="date" tick={{ fontSize: 10, fill: mutedColor }} tickFormatter={(v: string) => v.slice(5)} />
                    <YAxis tick={{ fontSize: 10, fill: mutedColor }} />
                    <Tooltip contentStyle={{ background: isDark ? '#1a1a2e' : '#fff', border: 'none', borderRadius: 12, fontSize: 11 }} />
                    <Area type="monotone" dataKey="count" stroke="#6366f1" fill="url(#colorQueries)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Search Success Donut */}
              <div className="glass-panel p-4">
                <h3 className="text-xs font-semibold mb-4 flex items-center gap-2" style={{ color: textColor }}>
                  <PieIcon size={14} style={{ color: 'var(--accent-primary)' }} />
                  Search Success Rate
                </h3>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Matched', value: stats.successful_matches },
                        { name: 'Fallback', value: stats.total_queries - stats.successful_matches },
                      ]}
                      cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={4} dataKey="value"
                    >
                      <Cell fill="#22c55e" />
                      <Cell fill="#ef4444" />
                    </Pie>
                    <Tooltip contentStyle={{ background: isDark ? '#1a1a2e' : '#fff', border: 'none', borderRadius: 12, fontSize: 11 }} />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Category Stats */}
            <div className="glass-panel p-4">
              <h3 className="text-xs font-semibold mb-4 flex items-center gap-2" style={{ color: textColor }}>
                <BarChart3 size={14} style={{ color: 'var(--accent-primary)' }} />
                Most Queried Categories
              </h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={catStats} layout="vertical" margin={{ left: 100 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#1a1a2e' : '#e0e0f0'} />
                  <XAxis type="number" tick={{ fontSize: 10, fill: mutedColor }} />
                  <YAxis type="category" dataKey="category" tick={{ fontSize: 10, fill: mutedColor }} width={100} />
                  <Tooltip contentStyle={{ background: isDark ? '#1a1a2e' : '#fff', border: 'none', borderRadius: 12, fontSize: 11 }} />
                  <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                    {catStats.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {tab === 'manage' && (
          <div className="space-y-4 max-w-6xl mx-auto">
            {/* Toolbar */}
            <div className="flex items-center gap-3">
              <div className="flex-1 glass-panel flex items-center gap-2 px-3 py-2">
                <Search size={14} style={{ color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  placeholder="Search FAQs..."
                  className="flex-1 bg-transparent outline-none text-sm"
                  style={{ color: 'var(--text-primary)' }}
                />
              </div>
              <motion.button
                onClick={() => setShowCreate(true)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-4 py-2 rounded-xl text-xs font-medium text-white flex items-center gap-2"
                style={{ background: 'var(--accent-primary)' }}
              >
                <Plus size={14} /> Add FAQ
              </motion.button>
              {selectedIds.size > 0 && (
                <motion.button
                  onClick={handleBulkDelete}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  whileHover={{ scale: 1.05 }}
                  className="px-4 py-2 rounded-xl text-xs font-medium text-white flex items-center gap-2 bg-red-500"
                >
                  <Trash2 size={14} /> Delete ({selectedIds.size})
                </motion.button>
              )}
            </div>

            {/* Create Modal */}
            <AnimatePresence>
              {showCreate && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="glass-elevated p-4 space-y-3 overflow-hidden"
                >
                  <h3 className="text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>New FAQ</h3>
                  <select
                    value={newFaq.category_id}
                    onChange={e => setNewFaq({ ...newFaq, category_id: Number(e.target.value) })}
                    className="w-full p-2 rounded-lg text-xs bg-transparent border"
                    style={{ borderColor: 'var(--border-glass)', color: 'var(--text-primary)' }}
                  >
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                  <input
                    value={newFaq.question}
                    onChange={e => setNewFaq({ ...newFaq, question: e.target.value })}
                    placeholder="Question..."
                    className="w-full p-2 rounded-lg text-xs bg-transparent border"
                    style={{ borderColor: 'var(--border-glass)', color: 'var(--text-primary)' }}
                  />
                  <textarea
                    value={newFaq.answer}
                    onChange={e => setNewFaq({ ...newFaq, answer: e.target.value })}
                    placeholder="Answer..."
                    rows={3}
                    className="w-full p-2 rounded-lg text-xs bg-transparent border resize-none"
                    style={{ borderColor: 'var(--border-glass)', color: 'var(--text-primary)' }}
                  />
                  <div className="flex gap-2 justify-end">
                    <button onClick={() => setShowCreate(false)} className="px-3 py-1.5 rounded-lg text-xs" style={{ color: 'var(--text-muted)' }}>Cancel</button>
                    <button onClick={handleCreate} className="px-3 py-1.5 rounded-lg text-xs text-white" style={{ background: 'var(--accent-primary)' }}>Create</button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* FAQ Table */}
            <div className="glass-panel overflow-hidden">
              <table className="w-full text-xs">
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-glass)' }}>
                    <th className="py-3 px-3 text-left w-8">
                      <input
                        type="checkbox"
                        onChange={e => {
                          if (e.target.checked) setSelectedIds(new Set(faqs.map(f => f.id)));
                          else setSelectedIds(new Set());
                        }}
                        checked={selectedIds.size === faqs.length && faqs.length > 0}
                      />
                    </th>
                    <th className="py-3 px-3 text-left font-semibold" style={{ color: 'var(--text-secondary)' }}>ID</th>
                    <th className="py-3 px-3 text-left font-semibold" style={{ color: 'var(--text-secondary)' }}>Category</th>
                    <th className="py-3 px-3 text-left font-semibold" style={{ color: 'var(--text-secondary)' }}>Question</th>
                    <th className="py-3 px-3 text-left font-semibold" style={{ color: 'var(--text-secondary)' }}>Views</th>
                    <th className="py-3 px-3 text-right font-semibold" style={{ color: 'var(--text-secondary)' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {faqs.slice(0, 50).map(faq => (
                    <tr key={faq.id} className="hover:bg-white/5 transition-colors" style={{ borderBottom: '1px solid var(--border-glass)' }}>
                      <td className="py-2.5 px-3">
                        <input type="checkbox" checked={selectedIds.has(faq.id)} onChange={() => toggleSelect(faq.id)} />
                      </td>
                      <td className="py-2.5 px-3 font-mono" style={{ color: 'var(--text-muted)' }}>{faq.id}</td>
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 rounded-full text-[10px]" style={{ background: 'var(--accent-primary)', color: 'white', opacity: 0.8 }}>
                          {faq.category_name}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 max-w-xs">
                        {editingId === faq.id ? (
                          <input
                            value={editData.question}
                            onChange={e => setEditData({ ...editData, question: e.target.value })}
                            className="w-full p-1 rounded text-xs bg-transparent border"
                            style={{ borderColor: 'var(--border-glass)', color: 'var(--text-primary)' }}
                          />
                        ) : (
                          <span className="truncate block" style={{ color: 'var(--text-primary)' }}>
                            {faq.question.length > 65 ? faq.question.slice(0, 65) + '...' : faq.question}
                          </span>
                        )}
                      </td>
                      <td className="py-2.5 px-3 font-mono" style={{ color: 'var(--text-muted)' }}>{faq.view_count}</td>
                      <td className="py-2.5 px-3 text-right">
                        <div className="flex items-center justify-end gap-1">
                          {editingId === faq.id ? (
                            <>
                              <button onClick={handleSaveEdit} className="p-1 rounded hover:bg-green-500/10"><Save size={13} style={{ color: '#22c55e' }} /></button>
                              <button onClick={() => setEditingId(null)} className="p-1 rounded hover:bg-red-500/10"><X size={13} style={{ color: '#ef4444' }} /></button>
                            </>
                          ) : (
                            <>
                              <button
                                onClick={() => { setEditingId(faq.id); setEditData({ question: faq.question, answer: faq.answer, category_id: faq.category_id }); }}
                                className="p-1 rounded hover:bg-indigo-500/10"
                              >
                                <Edit3 size={13} style={{ color: 'var(--accent-primary)' }} />
                              </button>
                              <button onClick={() => handleDelete(faq.id)} className="p-1 rounded hover:bg-red-500/10">
                                <Trash2 size={13} style={{ color: '#ef4444' }} />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {faqs.length === 0 && (
                <div className="text-center py-12">
                  <AlertCircle size={32} className="mx-auto mb-2 opacity-20" />
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>No FAQs found</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
