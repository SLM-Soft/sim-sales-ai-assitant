import HomePage from './pages/HomePage';
import { useEffect } from 'react';
import { useChatStore } from './store/chatStore';

export default function App() {
  const theme = useChatStore((s) => s.theme);

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('theme-dark', 'theme-light', 'theme-neutral');
    root.classList.add(`theme-${theme}`);
  }, [theme]);

  return <HomePage />;
}
