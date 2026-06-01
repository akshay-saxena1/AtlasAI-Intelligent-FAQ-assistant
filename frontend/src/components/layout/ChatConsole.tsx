import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Mic, MicOff, Volume2, VolumeX, ThumbsUp, ThumbsDown, BookmarkPlus, Sparkles, Search } from 'lucide-react';
import { useTypingEffect, useVoice } from '../../hooks';
import {
  sendMessage, getTypeahead, submitFeedback, createBookmark,
  type ChatResponse, type TypeaheadSuggestion, type SuggestionItem
} from '../../api/client';

interface Message {
  id: string;
  role: 'user' | 'bot';
  text: string;
  timestamp: Date;
  response?: ChatResponse;
  isNew?: boolean;
}

interface ChatConsoleProps {
  sessionId: string;
  selectedCategory: string | null;
  onResponse: (response: ChatResponse | null) => void;
}

function BotBubble({ message, onSpeak, onFeedback, onBookmark }: {
  message: Message;
  onSpeak: (text: string) => void;
  onFeedback: (chatId: number, helpful: boolean) => void;
  onBookmark: (faqId: number) => void;
}) {
  const { displayText, isTyping } = useTypingEffect(message.text, 15, !!message.isNew);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      className="flex gap-3 max-w-[85%]"
    >
      <div className="w-8 h-8 rounded-xl accent-gradient flex items-center justify-center flex-shrink-0 mt-1">
        <Sparkles size={14} className="text-white" />
      </div>
      <div>
        <div
          className="glass-panel px-4 py-3 text-sm leading-relaxed"
          style={{ color: 'var(--text-primary)' }}
        >
          <span className={isTyping ? 'typing-cursor' : ''}>{displayText}</span>
        </div>
        {!isTyping && message.response && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-1 mt-1.5 ml-1"
          >
            {message.response.chat_id > 0 && (
              <>
                <button
                  onClick={() => onFeedback(message.response!.chat_id, true)}
                  className="p-1 rounded-md hover:bg-green-500/10 transition-colors"
                  style={{ color: 'var(--text-muted)' }}
                  title="Helpful"
                >
                  <ThumbsUp size={12} />
                </button>
                <button
                  onClick={() => onFeedback(message.response!.chat_id, false)}
                  className="p-1 rounded-md hover:bg-red-500/10 transition-colors"
                  style={{ color: 'var(--text-muted)' }}
                  title="Not helpful"
                >
                  <ThumbsDown size={12} />
                </button>
              </>
            )}
            {message.response.faq_id && (
              <button
                onClick={() => onBookmark(message.response!.faq_id!)}
                className="p-1 rounded-md hover:bg-indigo-500/10 transition-colors"
                style={{ color: 'var(--text-muted)' }}
                title="Bookmark"
              >
                <BookmarkPlus size={12} />
              </button>
            )}
            <button
              onClick={() => onSpeak(message.text)}
              className="p-1 rounded-md hover:bg-indigo-500/10 transition-colors"
              style={{ color: 'var(--text-muted)' }}
              title="Read aloud"
            >
              <Volume2 size={12} />
            </button>
            <span className="text-[10px] ml-2" style={{ color: 'var(--text-muted)' }}>
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}

export default function ChatConsole({ sessionId, selectedCategory, onResponse }: ChatConsoleProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'bot',
      text: "Hello! 👋 I'm AtlasAI, your intelligent  FAQ assistant. Ask me anything about accounts, orders, billing, technical support, and more. I use advanced NLP to understand your questions and find the best answers.",
      timestamp: new Date(),
      isNew: true,
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [typeahead, setTypeahead] = useState<TypeaheadSuggestion[]>([]);
  const [showTypeahead, setShowTypeahead] = useState(false);
  const [quickSuggestions, setQuickSuggestions] = useState<string[]>([
    'How do I reset my password?',
    'What is your return policy?',
    'How do I track my order?',
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { isListening, transcript, startListening, speak, stopSpeaking, isSpeaking, isSupported } = useVoice();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (transcript) {
      setInput(transcript);
    }
  }, [transcript]);

  const handleTypeahead = useCallback(async (value: string) => {
    if (value.length >= 3) {
      try {
        const suggestions = await getTypeahead(value);
        setTypeahead(suggestions);
        setShowTypeahead(suggestions.length > 0);
      } catch {
        setShowTypeahead(false);
      }
    } else {
      setShowTypeahead(false);
    }
  }, []);

  const handleSend = useCallback(async (text?: string) => {
    const query = (text || input).trim();
    if (!query || isLoading) return;

    setInput('');
    setShowTypeahead(false);

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      text: query,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendMessage(query, sessionId);

      const botMessage: Message = {
        id: `bot_${Date.now()}`,
        role: 'bot',
        text: response.answer,
        timestamp: new Date(),
        response,
        isNew: true,
      };
      setMessages(prev => [...prev, botMessage]);
      onResponse(response);

      // Update quick suggestions from runner-ups
      if (response.suggestions.length > 0) {
        setQuickSuggestions(
          response.suggestions.slice(0, 3).map((s: SuggestionItem) => s.question)
        );
      }
    } catch {
      const errorMessage: Message = {
        id: `err_${Date.now()}`,
        role: 'bot',
        text: "I'm sorry, I encountered an error processing your request. Please try again or check if the backend server is running.",
        timestamp: new Date(),
        isNew: true,
      };
      setMessages(prev => [...prev, errorMessage]);
      onResponse(null);
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, sessionId, onResponse]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFeedback = async (chatId: number, helpful: boolean) => {
    try { await submitFeedback(chatId, helpful); } catch { /* silent */ }
  };

  const handleBookmark = async (faqId: number) => {
    try { await createBookmark(sessionId, faqId); } catch { /* silent */ }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        <AnimatePresence mode="popLayout">
          {messages.map(msg =>
            msg.role === 'user' ? (
              <motion.div
                key={msg.id}
                layout
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                className="flex justify-end"
              >
                <div
                  className="max-w-[70%] px-4 py-3 rounded-2xl rounded-br-md text-sm text-white"
                  style={{ background: 'var(--user-bubble-bg)' }}
                >
                  {msg.text}
                  <div className="text-[10px] text-white/50 mt-1 text-right">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </motion.div>
            ) : (
              <BotBubble
                key={msg.id}
                message={msg}
                onSpeak={speak}
                onFeedback={handleFeedback}
                onBookmark={handleBookmark}
              />
            )
          )}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3"
          >
            <div className="w-8 h-8 rounded-xl accent-gradient flex items-center justify-center flex-shrink-0">
              <Sparkles size={14} className="text-white animate-pulse" />
            </div>
            <div className="glass-panel px-4 py-3 flex items-center gap-1.5">
              {[0, 1, 2].map(i => (
                <motion.div
                  key={i}
                  className="w-2 h-2 rounded-full"
                  style={{ background: 'var(--accent-primary)' }}
                  animate={{ y: [0, -6, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
                />
              ))}
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Suggestion Chips */}
      <div className="px-6 py-2 flex gap-2 overflow-x-auto">
        {quickSuggestions.map((suggestion, i) => (
          <motion.button
            key={i}
            onClick={() => handleSend(suggestion)}
            className="glass-panel glass-panel-hover px-3 py-1.5 rounded-full text-[11px] whitespace-nowrap flex-shrink-0 font-medium"
            style={{ color: 'var(--accent-primary)' }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
          >
            {suggestion.length > 45 ? suggestion.slice(0, 45) + '...' : suggestion}
          </motion.button>
        ))}
      </div>

      {/* Input Bar */}
      <div className="px-6 pb-4 pt-2 relative">
        {/* Typeahead Dropdown */}
        <AnimatePresence>
          {showTypeahead && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="absolute bottom-full left-6 right-6 mb-2 glass-elevated overflow-hidden z-20"
            >
              {typeahead.map((item, i) => (
                <button
                  key={item.faq_id}
                  onClick={() => { setInput(item.question); setShowTypeahead(false); handleSend(item.question); }}
                  className="w-full text-left px-4 py-2.5 text-sm hover:bg-white/5 transition-colors flex items-center gap-3 border-b last:border-0"
                  style={{ borderColor: 'var(--border-glass)', color: 'var(--text-primary)' }}
                >
                  <Search size={13} style={{ color: 'var(--text-muted)' }} />
                  <div className="flex-1 truncate">
                    <p className="truncate">{item.question}</p>
                    <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{item.category}</p>
                  </div>
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        <div className="glass-elevated flex items-center gap-3 px-4 py-3">
          {isSupported && (
            <motion.button
              id="voice-toggle"
              onClick={isListening ? () => { } : startListening}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-1.5 rounded-lg transition-colors"
              style={{
                background: isListening ? 'var(--error)' : 'transparent',
                color: isListening ? 'white' : 'var(--text-muted)',
              }}
            >
              {isListening ? <MicOff size={16} /> : <Mic size={16} />}
            </motion.button>
          )}

          <input
            ref={inputRef}
            id="chat-input"
            type="text"
            value={input}
            onChange={(e) => { setInput(e.target.value); handleTypeahead(e.target.value); }}
            onKeyDown={handleKeyDown}
            onFocus={() => input.length >= 3 && setShowTypeahead(typeahead.length > 0)}
            onBlur={() => setTimeout(() => setShowTypeahead(false), 200)}
            placeholder="Ask me anything..."
            className="flex-1 bg-transparent outline-none text-sm"
            style={{ color: 'var(--text-primary)' }}
            disabled={isLoading}
          />

          {isSpeaking && (
            <motion.button
              onClick={stopSpeaking}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-1.5 rounded-lg"
              style={{ color: 'var(--accent-primary)' }}
            >
              <VolumeX size={16} />
            </motion.button>
          )}

          <motion.button
            id="send-button"
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            className="p-2 rounded-xl transition-all"
            style={{
              background: input.trim() ? 'var(--accent-gradient)' : 'transparent',
              color: input.trim() ? 'white' : 'var(--text-muted)',
              opacity: input.trim() ? 1 : 0.5,
            }}
          >
            <Send size={16} />
          </motion.button>
        </div>
      </div>
    </div>
  );
}
