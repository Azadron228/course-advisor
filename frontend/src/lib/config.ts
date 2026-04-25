export const getApiBaseUrl = () => {
  // If we're on the client (browser)
  if (typeof window !== 'undefined') {
    // If the environment variable is set, use it. 
    // Usually this would be http://localhost:2828/api/v1 for local browser access
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:2828/api/v1';
  }
  
  // If we're on the server
  // When running in Docker, we might need http://backend:8000/api/v1
  return process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:2828/api/v1';
};

export const API_BASE_URL = getApiBaseUrl();
