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
    apiClient.get<AuthUser>('/user/profile')
      .then((res) => {
        setUser(res.data);
        setLoading(false);
      })
      .catch(() => {
        apiClient.setToken(null);
        setUser(null);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (username: string, password: string) => {
    const res = await apiClient.post<{ access_token: string; token_type: string; expires_in: number; user: AuthUser }>(
      '/auth/login',
      { username, password }
    );
    apiClient.setToken(res.data.access_token);
    setUser(res.data.user);
    return res.data;
  };

  const register = async (data: { username: string; email: string; password: string; full_name?: string }) => {
    const res = await apiClient.post<{ access_token: string; token_type: string; expires_in: number; user: AuthUser }>(
      '/auth/register',
      data
    );
    apiClient.setToken(res.data.access_token);
    setUser(res.data.user);
    return res.data;
  };

  const logout = () => {
    apiClient.setToken(null);
    setUser(null);
    router.push('/login');
  };

  return { user, loading, login, register, logout, isAuthenticated: !!user };
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
