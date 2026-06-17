import { useCallback } from 'react';
import { useWorkflowVersion } from '../contexts/WorkflowVersionContext';
import { getApiBaseUrl } from '../config/workflowConfig';

interface ApiOptions extends RequestInit {
  params?: Record<string, string | number | boolean>;
}

/**
 * Custom hook for making API calls that respect the selected workflow version
 */
export function useApi() {
  const { version } = useWorkflowVersion();

  const getBaseUrl = useCallback(() => {
    return getApiBaseUrl(version);
  }, [version]);

  /**
   * Build full URL for an endpoint
   */
  const buildUrl = useCallback((endpoint: string, params?: Record<string, string | number | boolean>): string => {
    const baseUrl = getBaseUrl();
    let url = `${baseUrl}${endpoint}`;
    
    if (params && Object.keys(params).length > 0) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.set(key, String(value));
        }
      });
      url += `?${searchParams.toString()}`;
    }
    
    return url;
  }, [getBaseUrl]);

  /**
   * Generic API request method
   */
  const request = useCallback(async <T = any>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH',
    endpoint: string,
    data?: any,
    options: ApiOptions = {}
  ): Promise<T> => {
    const url = buildUrl(endpoint);
    
    const token = localStorage.getItem('token');
    
    const config: RequestInit = {
      ...options,
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers,
      },
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      config.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error || errorData.message || `HTTP error! status: ${response.status}`
        );
      }

      // Try to parse as JSON, fall back to text
      try {
        return await response.json();
      } catch {
        return response.text() as T;
      }
    } catch (error) {
      console.error(`API Error [${method} ${endpoint}]:`, error);
      throw error;
    }
  }, [buildUrl]);

  /**
   * Convenience methods for common HTTP verbs
   */
  const get = useCallback(<T = any>(endpoint: string, params?: Record<string, string | number | boolean>) => {
    return request<T>('GET', endpoint, undefined, { params });
  }, [request]);

  const post = useCallback(<T = any>(endpoint: string, data?: any, options?: ApiOptions) => {
    return request<T>('POST', endpoint, data, options);
  }, [request]);

  const put = useCallback(<T = any>(endpoint: string, data?: any, options?: ApiOptions) => {
    return request<T>('PUT', endpoint, data, options);
  }, [request]);

  const del = useCallback(<T = any>(endpoint: string, options?: ApiOptions) => {
    return request<T>('DELETE', endpoint, undefined, options);
  }, [request]);

  const patch = useCallback(<T = any>(endpoint: string, data?: any, options?: ApiOptions) => {
    return request<T>('PATCH', endpoint, data, options);
  }, [request]);

  return {
    getBaseUrl,
    buildUrl,
    request,
    get,
    post,
    put,
    del,
    patch,
  };
}

export default useApi;
