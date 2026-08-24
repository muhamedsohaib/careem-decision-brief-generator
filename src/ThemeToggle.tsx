import { Moon, Sun } from 'lucide-react';
import { useEffect, useState } from 'react';

type Theme = 'light' | 'dark';
const STORAGE_KEY = 'decision-brief-theme';

function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return 'light';
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') return stored;
  } catch {
    // Storage can be unavailable in hardened browser modes.
  }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);
  const dark = theme === 'dark';

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
    try {
      window.localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // Theme still works for the current session when storage is unavailable.
    }
  }, [theme]);

  return <button className='theme-toggle' type='button' onClick={() => setTheme(dark ? 'light' : 'dark')} aria-label={`Switch to ${dark ? 'light' : 'dark'} theme`} aria-pressed={dark}>{dark ? <Sun size={15} aria-hidden='true' /> : <Moon size={15} aria-hidden='true' />}<span>{dark ? 'Light' : 'Dark'}</span></button>;
}
