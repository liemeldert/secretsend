import { useState, useEffect } from 'react';
import { ApiResponse } from './route';

export function useConfig(): [ApiResponse, boolean] {
  const [data, setData] = useState<ApiResponse>({ backend_url: "", turnstyle_siteid: "" });
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/config/');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const responseData = await response.json();
        setData(responseData);
      } catch (error) {
        console.error('Fetch error:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []); // Empty dependency array to run only once on mount

  return [data, loading];
}