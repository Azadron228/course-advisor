'use client';

import { useState, useEffect, useCallback } from 'react';
import Cookies from 'js-cookie';
import { apiClient } from '@/lib/api-client';
import { useRouter } from 'next/navigation';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  career_goal?: string;
  interests?: string[];
  onboarding_completed?: boolean;
  is_active: boolean;
  is_superuser: boolean;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const fetchUser = useCallback(async () => {
    const token = Cookies.get('token');
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const userData = await apiClient.get<User>('/auth/me');
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      Cookies.remove('token');
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const data = await apiClient.post<TokenResponse>('/auth/token', formData);
      Cookies.set('token', data.access_token, { expires: 7 }); // Set cookie for 7 days
      await fetchUser();
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = () => {
    Cookies.remove('token');
    setUser(null);
    router.push('/login');
  };

  return {
    user,
    isLoading,
    login,
    logout,
    fetchUser,
    isAuthenticated: !!user,
  };
}
