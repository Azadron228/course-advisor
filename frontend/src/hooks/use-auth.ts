'use client';

import { useState, useEffect, useCallback } from 'react';
import Cookies from 'js-cookie';
import { apiClient } from '@/lib/api-client';
import { useRouter } from '@/i18n/routing';

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
    // Ensure state updates happen after the first render to avoid cascading renders
    await Promise.resolve();
    
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
    const timer = setTimeout(() => {
      fetchUser();
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchUser]);

  const login = async (username: string, password: string) => {
    console.log('Attempting login for:', username);
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
      console.log('Sending request to /auth/token...');
      const data = await apiClient.post<TokenResponse>('/auth/token', formData);
      console.log('Login successful, token received');
      Cookies.set('token', data.access_token, { expires: 7 }); // Set cookie for 7 days
      console.log('Fetching user data...');
      await fetchUser();
      console.log('User data fetched, navigating to dashboard');
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed in useAuth:', error);
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
