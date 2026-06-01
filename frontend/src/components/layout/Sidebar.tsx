import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare, History, Bookmark, Settings, ChevronLeft, ChevronRight,
  Search, Shield, LayoutDashboard, Sparkles, HelpCircle, Package,
  CreditCard, Smartphone, Lock, RotateCcw, Building2
} from 'lucide-react';
import { type Category, getCategories, getBookmarks, type Bookmark as BookmarkType } from '../../api/client';

const categoryIcons: Record<string, React.ReactNode> = {
  'Account Management': <HelpCircle size={16} />,
  'Orders & Shipping': <Package size={16} />,
  'Technical Support': <Settings size={16} />,
  'Billing & Payments': <CreditCard size={16} />,
  'Product Information': <Smartphone size={16} />,
  'Security & Privacy': <Lock size={16} />,
  'Returns & Refunds': <RotateCcw size={16} />,
  'General & Company': <Building2 size={16} />,
};

interface SidebarProps {
  onCategorySelect: (category: string | null) => void;
  selectedCategory: string | null;
  sessionId: string;
  onAdminClick: () => void;
  isAdmin: boolean;
}

export default function Sidebar({ onCategorySelect, selectedCategory, sessionId, onAdminClick, isAdmin }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [bookmarks, setBookmarks] = useState<BookmarkType[]>([]);
  const [activeTab, setActiveTab] = useState<'categories' | 'history' | 'bookmarks'>('categories');

  useEffect(() => {
    getCategories().then(setCategories).catch(() => { });
    getBookmarks(sessionId).then(setBookmarks).catch(() => { });
  }, [sessionId]);

  const sidebarVariants = {
    expanded: { width: 280 },
    collapsed: { width: 68 },
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: (i: number) => ({
      opacity: 1, x: 0,
      transition: { delay: i * 0.05, type: 'spring', stiffness: 300, damping: 24 },
    }),
  };

  return (
    <motion.aside
      id="sidebar-nav"
      variants={sidebarVariants}
      animate={collapsed ? 'collapsed' : 'expanded'}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="h-full glass-panel flex flex-col overflow-hidden relative"
      style={{ borderRadius: 0, borderRight: '1px solid var(--border-glass)' }}
    >
      {/* Header */}
      <div className="p-4 flex items-center gap-3 border-b" style={{ borderColor: 'var(--border-glass)' }}>
        <motion.div
          className="w-9 h-9 rounded-xl accent-gradient flex items-center justify-center flex-shrink-0"
          whileHover={{ scale: 1.1, rotate: 5 }}
          whileTap={{ scale: 0.95 }}
        >
          <Sparkles size={18} className="text-white" />
        </motion.div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: 'auto' }}
              exit={{ opacity: 0, width: 0 }}
              className="overflow-hidden whitespace-nowrap"
            >
              <h1 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>AtlasAI</h1>
              <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Powered by AI</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Tab Switcher */}
      {!collapsed && (
        <div className="flex p-2 gap-1">
          {[
            { key: 'categories' as const, icon: <Search size={14} />, label: 'Topics' },
            { key: 'history' as const, icon: <History size={14} />, label: 'History' },
            { key: 'bookmarks' as const, icon: <Bookmark size={14} />, label: 'Saved' },
          ].map(tab => (
            <button
              key={tab.key}
              id={`sidebar-tab-${tab.key}`}
              onClick={() => setActiveTab(tab.key)}
              className="flex-1 py-1.5 px-2 rounded-lg text-[11px] font-medium flex items-center justify-center gap-1.5 transition-all"
              style={{
                background: activeTab === tab.key ? 'var(--accent-primary)' : 'transparent',
                color: activeTab === tab.key ? 'white' : 'var(--text-secondary)',
              }}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {activeTab === 'categories' && (
          <>
            <motion.button
              onClick={() => onCategorySelect(null)}
              className="w-full text-left py-2 px-3 rounded-xl text-xs font-medium transition-all flex items-center gap-2.5"
              style={{
                background: selectedCategory === null ? 'var(--accent-primary)' : 'transparent',
                color: selectedCategory === null ? 'white' : 'var(--text-secondary)',
              }}
              whileHover={{ x: 4 }}
              whileTap={{ scale: 0.98 }}
            >
              <MessageSquare size={15} />
              {!collapsed && 'All Categories'}
            </motion.button>
            {categories.map((cat, i) => (
              <motion.button
                key={cat.id}
                custom={i}
                variants={itemVariants}
                initial="hidden"
                animate="visible"
                onClick={() => onCategorySelect(cat.name)}
                className="w-full text-left py-2 px-3 rounded-xl text-xs transition-all flex items-center gap-2.5 group"
                style={{
                  background: selectedCategory === cat.name ? 'var(--accent-primary)' : 'transparent',
                  color: selectedCategory === cat.name ? 'white' : 'var(--text-secondary)',
                }}
                whileHover={{ x: 4 }}
                whileTap={{ scale: 0.98 }}
              >
                {categoryIcons[cat.name] || <HelpCircle size={15} />}
                {!collapsed && (
                  <>
                    <span className="flex-1 truncate">{cat.name}</span>
                    <span className="text-[10px] opacity-60">{cat.faq_count}</span>
                  </>
                )}
              </motion.button>
            ))}
          </>
        )}

        {activeTab === 'bookmarks' && !collapsed && (
          bookmarks.length === 0 ? (
            <div className="text-center py-8 text-xs" style={{ color: 'var(--text-muted)' }}>
              <Bookmark size={24} className="mx-auto mb-2 opacity-30" />
              No saved bookmarks yet
            </div>
          ) : (
            bookmarks.map((bm, i) => (
              <motion.div
                key={bm.id}
                custom={i}
                variants={itemVariants}
                initial="hidden"
                animate="visible"
                className="py-2 px-3 rounded-xl text-xs cursor-pointer glass-panel-hover"
                style={{ color: 'var(--text-secondary)' }}
              >
                <p className="truncate font-medium" style={{ color: 'var(--text-primary)' }}>{bm.question}</p>
                <p className="text-[10px] mt-0.5" style={{ color: 'var(--text-muted)' }}>{bm.category}</p>
              </motion.div>
            ))
          )
        )}

        {activeTab === 'history' && !collapsed && (
          <div className="text-center py-8 text-xs" style={{ color: 'var(--text-muted)' }}>
            <History size={24} className="mx-auto mb-2 opacity-30" />
            Chat history appears here
          </div>
        )}
      </div>

      {/* Admin Button */}
      <div className="p-2 border-t" style={{ borderColor: 'var(--border-glass)' }}>
        <motion.button
          id="admin-toggle"
          onClick={onAdminClick}
          className="w-full py-2 px-3 rounded-xl text-xs font-medium flex items-center gap-2.5 transition-all"
          style={{
            background: isAdmin ? 'var(--accent-primary)' : 'transparent',
            color: isAdmin ? 'white' : 'var(--text-secondary)',
          }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <LayoutDashboard size={15} />
          {!collapsed && 'Admin Dashboard'}
        </motion.button>
      </div>

      {/* Collapse Toggle */}
      <motion.button
        id="sidebar-collapse"
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-1/2 w-6 h-6 rounded-full flex items-center justify-center z-10"
        style={{
          background: 'var(--accent-primary)',
          color: 'white',
          transform: 'translateY(-50%)',
        }}
        whileHover={{ scale: 1.15 }}
        whileTap={{ scale: 0.9 }}
      >
        {collapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </motion.button>
    </motion.aside>
  );
}
