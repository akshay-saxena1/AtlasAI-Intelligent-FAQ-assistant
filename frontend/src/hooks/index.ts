import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for simulating a human-cadence typing effect.
 * Characters are revealed one by one with variable speed.
 */
export function useTypingEffect(
  text: string,
  speed: number = 20,
  enabled: boolean = true
): { displayText: string; isTyping: boolean } {
  const [displayText, setDisplayText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!enabled || !text) {
      setDisplayText(text);
      setIsTyping(false);
      return;
    }

    setIsTyping(true);
    setDisplayText('');
    let index = 0;

    const interval = setInterval(() => {
      if (index < text.length) {
        setDisplayText(text.slice(0, index + 1));
        index++;
      } else {
        setIsTyping(false);
        clearInterval(interval);
      }
    }, speed + Math.random() * 15); // Variable speed for human cadence

    return () => clearInterval(interval);
  }, [text, speed, enabled]);

  return { displayText, isTyping };
}

/**
 * Custom hook for OS-preference-aware dark/light theme toggling.
 * Persists preference to localStorage and syncs CSS class.
 */
export function useTheme(): {
  isDark: boolean;
  toggle: () => void;
} {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved) return saved === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  // Listen for OS theme changes
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('theme')) {
        setIsDark(e.matches);
      }
    };
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  const toggle = useCallback(() => setIsDark(prev => !prev), []);

  return { isDark, toggle };
}

/**
 * Custom hook for Web Speech API integration.
 * Provides voice-to-text dictation and text-to-speech synthesis.
 */
export function useVoice(): {
  isListening: boolean;
  transcript: string;
  startListening: () => void;
  stopListening: () => void;
  speak: (text: string) => void;
  stopSpeaking: () => void;
  isSpeaking: boolean;
  isSupported: boolean;
} {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);

  const SpeechRecognition =
    (window as unknown as Record<string, unknown>).SpeechRecognition ||
    (window as unknown as Record<string, unknown>).webkitSpeechRecognition;

  const isSupported = !!SpeechRecognition && !!window.speechSynthesis;

  const startListening = useCallback(() => {
    if (!SpeechRecognition) return;

    const recognition = new (SpeechRecognition as new () => SpeechRecognition)();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const result = event.results[0][0].transcript;
      setTranscript(result);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);

    recognition.start();
  }, [SpeechRecognition]);

  const stopListening = useCallback(() => {
    setIsListening(false);
  }, []);

  const speak = useCallback((text: string) => {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
  }, []);

  const stopSpeaking = useCallback(() => {
    window.speechSynthesis?.cancel();
    setIsSpeaking(false);
  }, []);

  return {
    isListening,
    transcript,
    startListening,
    stopListening,
    speak,
    stopSpeaking,
    isSpeaking,
    isSupported,
  };
}

/**
 * Hook to generate and persist a unique session ID.
 */
export function useSession(): string {
  const [sessionId] = useState(() => {
    const saved = sessionStorage.getItem('chatSessionId');
    if (saved) return saved;
    const id = `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
    sessionStorage.setItem('chatSessionId', id);
    return id;
  });
  return sessionId;
}
