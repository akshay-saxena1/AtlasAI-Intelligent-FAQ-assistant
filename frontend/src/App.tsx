import React, { useState } from 'react';
import ChatPage from './pages/ChatPage';
import AdminPage from './pages/AdminPage';

/**
 * Root Application Component
 *
 * Manages top-level navigation between the Chat interface
 * and Admin Dashboard using simple state-based routing.
 *
 * Registration ID: Akshay Saxena
 */
export default function App() {
  const [isAdmin, setIsAdmin] = useState(false);

  if (isAdmin) {
    return <AdminPage onBack={() => setIsAdmin(false)} />;
  }

  return (
    <ChatPage
      onAdminClick={() => setIsAdmin(true)}
      isAdmin={isAdmin}
    />
  );
}
