'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from './types';
import { useRouter } from 'next/navigation';
import api from './api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      fetchUser(savedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUser = async (authToken: string) => {
    try {
      const response = await api.get('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setUser(response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user', error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (newToken: string) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    const userData = await fetchUser(newToken);
    if (userData?.is_admin) {
      router.push('/admin');
    } else {
      router.push('/dashboard');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
