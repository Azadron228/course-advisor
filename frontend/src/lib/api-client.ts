import Cookies from 'js-cookie';
import { API_BASE_URL } from './config';

export type ApiError = {
  message: string;
  status: number;
};

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    if (response.status === 401) {
      // Clear token and redirect to login if unauthorized
      Cookies.remove('token');
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    
    let errorMessage = 'An error occurred';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch (e) {
      // Fallback to status text
      errorMessage = response.statusText || errorMessage;
    }
    
    throw { message: errorMessage, status: response.status } as ApiError;
  }
  
  if (response.status === 204) {
    return {} as T;
  }
  
  return response.json();
}

export const apiClient = {
  async get<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = Cookies.get('token');
    const headers = {
      'Authorization': token ? `Bearer ${token}` : '',
      ...options.headers,
    };
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
    
    return handleResponse<T>(response);
  },
  
  async post<T>(endpoint: string, body: any, options: RequestInit = {}): Promise<T> {
    const token = Cookies.get('token');
    const isFormData = body instanceof FormData;
    const url = `${API_BASE_URL}${endpoint}`;
    
    console.log(`apiClient: Calling POST ${url}`);
    
    const headers: Record<string, string> = {
      'Authorization': token ? `Bearer ${token}` : '',
      ...((options.headers as Record<string, string>) || {}),
    };
    
    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        ...options,
        headers,
        body: isFormData ? body : JSON.stringify(body),
      });
      
      console.log(`apiClient: Received response ${response.status} ${response.statusText}`);
      return handleResponse<T>(response);
    } catch (error) {
      console.error('apiClient: Fetch error:', error);
      throw error;
    }
  },
  
  async put<T>(endpoint: string, body: any, options: RequestInit = {}): Promise<T> {
    const token = Cookies.get('token');
    const isFormData = body instanceof FormData;
    
    const headers: Record<string, string> = {
      'Authorization': token ? `Bearer ${token}` : '',
      ...((options.headers as Record<string, string>) || {}),
    };
    
    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      ...options,
      headers,
      body: isFormData ? body : JSON.stringify(body),
    });
    
    return handleResponse<T>(response);
  },
  
  async patch<T>(endpoint: string, body: any, options: RequestInit = {}): Promise<T> {
    const token = Cookies.get('token');
    const isFormData = body instanceof FormData;
    
    const headers: Record<string, string> = {
      'Authorization': token ? `Bearer ${token}` : '',
      ...((options.headers as Record<string, string>) || {}),
    };
    
    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PATCH',
      ...options,
      headers,
      body: isFormData ? body : JSON.stringify(body),
    });
    
    return handleResponse<T>(response);
  },
  async delete<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = Cookies.get('token');
    const headers = {
      'Authorization': token ? `Bearer ${token}` : '',
      ...options.headers,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      ...options,
      headers,
    });

    return handleResponse<T>(response);
  },

  async stream(endpoint: string, body: any, onChunk: (chunk: string) => void, options: RequestInit = {}): Promise<void> {
    const token = Cookies.get('token');
    const url = `${API_BASE_URL}${endpoint}`;

    const headers: Record<string, string> = {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    const response = await fetch(url, {
      method: 'POST',
      ...options,
      headers,
      body: JSON.stringify({ ...body, stream: true }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw { message: errorData.detail || 'Streaming failed', status: response.status } as ApiError;
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('Response body is not readable');

    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      onChunk(chunk);
    }
  },
  };
