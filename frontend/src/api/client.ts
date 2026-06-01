/**
 * Axios API client for the CodeAlpha FAQ Chatbot backend.
 * Provides typed methods for all API endpoints.
 * Registration ID: Akshay Saxena
 */

import axios, { type AxiosInstance } from 'axios';

// Types
export interface SuggestionItem {
  faq_id: number;
  question: string;
  category: string;
  confidence: number;
  semantic_score: number;
  lexical_score: number;
}

export interface ChatResponse {
  match_found: boolean;
  answer: string;
  faq_id: number | null;
  question: string;
  category: string;
  confidence: number;
  semantic_score: number;
  lexical_score: number;
  suggestions: SuggestionItem[];
  chat_id: number;
}

export interface FAQ {
  id: number;
  category_id: number;
  category_name: string;
  question: string;
  answer: string;
  view_count: number;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  icon: string;
  faq_count: number;
}

export interface DashboardStats {
  total_queries: number;
  successful_matches: number;
  success_rate: number;
  total_faqs: number;
  total_feedback: number;
  positive_feedback: number;
  avg_confidence: number;
}

export interface QueryOverTime {
  date: string;
  count: number;
}

export interface CategoryStats {
  category: string;
  count: number;
}

export interface TypeaheadSuggestion {
  faq_id: number;
  question: string;
  category: string;
}

export interface Bookmark {
  id: number;
  session_id: string;
  faq_id: number;
  question: string;
  category: string;
  created_at: string;
}

export interface ChatHistoryItem {
  id: number;
  session_id: string;
  user_query: string;
  bot_response: string;
  confidence_score: number;
  matched_faq_id: number | null;
  semantic_score: number;
  lexical_score: number;
  created_at: string;
}

// API Client
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// Chat endpoints
export const sendMessage = async (query: string, sessionId: string): Promise<ChatResponse> => {
  const { data } = await api.post<ChatResponse>('/chat/', { query, session_id: sessionId });
  return data;
};

export const getTypeahead = async (query: string): Promise<TypeaheadSuggestion[]> => {
  const { data } = await api.get<TypeaheadSuggestion[]>('/chat/suggest', { params: { q: query } });
  return data;
};

export const getChatHistory = async (sessionId: string): Promise<ChatHistoryItem[]> => {
  const { data } = await api.get<ChatHistoryItem[]>(`/chat/history/${sessionId}`);
  return data;
};

// FAQ endpoints
export const getFAQs = async (categoryId?: number, search?: string): Promise<FAQ[]> => {
  const params: Record<string, unknown> = {};
  if (categoryId) params.category_id = categoryId;
  if (search) params.search = search;
  const { data } = await api.get<FAQ[]>('/faqs/', { params });
  return data;
};

export const createFAQ = async (faq: { category_id: number; question: string; answer: string }): Promise<FAQ> => {
  const { data } = await api.post<FAQ>('/faqs/', faq);
  return data;
};

export const updateFAQ = async (id: number, faq: { category_id?: number; question?: string; answer?: string }): Promise<FAQ> => {
  const { data } = await api.put<FAQ>(`/faqs/${id}`, faq);
  return data;
};

export const deleteFAQ = async (id: number): Promise<void> => {
  await api.delete(`/faqs/${id}`);
};

export const bulkDeleteFAQs = async (ids: number[]): Promise<void> => {
  await api.delete('/faqs/bulk/delete', { data: ids });
};

export const getCategories = async (): Promise<Category[]> => {
  const { data } = await api.get<Category[]>('/faqs/categories');
  return data;
};

// Analytics endpoints
export const getDashboardStats = async (): Promise<DashboardStats> => {
  const { data } = await api.get<DashboardStats>('/analytics/dashboard');
  return data;
};

export const getQueriesOverTime = async (days?: number): Promise<QueryOverTime[]> => {
  const { data } = await api.get<QueryOverTime[]>('/analytics/queries-over-time', { params: { days } });
  return data;
};

export const getCategoryStats = async (): Promise<CategoryStats[]> => {
  const { data } = await api.get<CategoryStats[]>('/analytics/categories');
  return data;
};

// Bookmark endpoints
export const getBookmarks = async (sessionId: string): Promise<Bookmark[]> => {
  const { data } = await api.get<Bookmark[]>(`/bookmarks/${sessionId}`);
  return data;
};

export const createBookmark = async (sessionId: string, faqId: number): Promise<Bookmark> => {
  const { data } = await api.post<Bookmark>('/bookmarks', { session_id: sessionId, faq_id: faqId });
  return data;
};

export const deleteBookmark = async (id: number): Promise<void> => {
  await api.delete(`/bookmarks/${id}`);
};

// Feedback endpoints
export const submitFeedback = async (chatId: number, isHelpful: boolean): Promise<void> => {
  await api.post('/feedback', { chat_id: chatId, is_helpful: isHelpful });
};

export default api;
