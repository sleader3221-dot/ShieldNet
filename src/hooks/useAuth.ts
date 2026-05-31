import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/router';
import { apiClient, ApiError } from '@/utils/api';

interface AuthUser {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

const USER_CACHE_KEY = 'shieldnet_user';
const DEMO_USERS: Record<string, AuthUser> = {
  admin: { id: '1', username: 'admin', email: 'admin@shieldnet.io', full_name: 'System Administrator', role: 'admin', is_active: true },
  analyst: { id: '2', username: 'analyst', email: 'analyst@shieldnet.io', full_name: 'Security Analyst', role: 'analyst', is_active: true },
  jdoe: { id: '3', username: 'jdoe', email: 'john@shieldnet.io', full_name: 'John Doe', role: 'user', is_active: true },
  asmith: { id: '4', username: 'asmith', email: 'alice@shieldnet.io', full_name: 'Alice Smith', role: 'user', is_active: true },
  bob: { id: '5', username: 'bob', email: 'bob@shieldnet.io', full_name: 'Bob Johnson', role: 'user', is_active: true },
};

function fakeToken(username: string): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify({ sub: username, exp: Date.now() / 1000 + 86400, iat: Date.now() / 1000 }));
  return `${header}.${payload}.demo_signature`;
}

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const checkAuth = useCallback(() => {
    const token = apiClient.getToken();
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    const cached = localStorage.getItem(USER_CACHE_KEY);
    if (cached) {
      try { setUser(JSON.parse(cached)); setLoading(false); return; } catch {}
    }
    apiClient.get<AuthUser>('/user/profile')
      .then((res) => {
        setUser(res.data);
        localStorage.setItem(USER_CACHE_KEY, JSON.stringify(res.data));
        setLoading(false);
      })
      .catch(() => {
        const stillCached = localStorage.getItem(USER_CACHE_KEY);
        if (stillCached) {
          try { setUser(JSON.parse(stillCached)); setLoading(false); return; } catch {}
        }
        apiClient.setToken(null);
        localStorage.removeItem(USER_CACHE_KEY);
        setUser(null);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const demoLogin = (username: string) => {
    const demoUser = DEMO_USERS[username];
    if (!demoUser) throw new Error('Unknown demo user');
    const token = fakeToken(username);
    apiClient.setToken(token);
    localStorage.setItem(USER_CACHE_KEY, JSON.stringify(demoUser));
    setUser(demoUser);
  };

  const login = async (username: string, password: string) => {
    const res = await apiClient.post<{ access_token: string; token_type: string; expires_in: number; user: AuthUser }>(
      '/auth/login',
      { username, password }
    );
    apiClient.setToken(res.data.access_token);
    localStorage.setItem(USER_CACHE_KEY, JSON.stringify(res.data.user));
    setUser(res.data.user);
    return res.data;
  };

  const register = async (data: { username: string; email: string; password: string; full_name?: string }) => {
    const res = await apiClient.post<{ access_token: string; token_type: string; expires_in: number; user: AuthUser }>(
      '/auth/register',
      data
    );
    apiClient.setToken(res.data.access_token);
    localStorage.setItem(USER_CACHE_KEY, JSON.stringify(res.data.user));
    setUser(res.data.user);
    return res.data;
  };

  const logout = () => {
    apiClient.setToken(null);
    localStorage.removeItem(USER_CACHE_KEY);
    setUser(null);
    router.push('/login');
  };

  return { user, loading, login, demoLogin, register, logout, isAuthenticated: !!user };
}

export function useAuthGuard() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace('/login');
    }
  }, [loading, user, router]);

  return { user, loading, isAuthenticated: !!user };
}
