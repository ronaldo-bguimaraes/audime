import { useState, useEffect, useRef, useCallback } from "react";

interface FetchState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useFetch<T>(
  fetcher: () => Promise<T>,
  deps: React.DependencyList = [],
) {
  const [state, setState] = useState<FetchState<T>>({
    data: null,
    loading: true,
    error: null,
  });
  const fetcherRef = useRef(fetcher);

  // Sync fetcher ref without violating rules of hooks
  useEffect(() => {
    fetcherRef.current = fetcher;
  });

  // Re-fetch when deps change
  useEffect(() => {
    let cancelled = false;

    if (!cancelled) {
      fetcherRef
        .current()
        .then((data) => {
          if (!cancelled) {
            setState({ data, loading: false, error: null });
          }
        })
        .catch((err: unknown) => {
          if (!cancelled) {
            const message =
              err instanceof Error ? err.message : "Erro desconhecido";
            setState({ data: null, loading: false, error: message });
          }
        });
    }

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  const refetch = useCallback(async () => {
    try {
      const data = await fetcherRef.current();
      setState({ data, loading: false, error: null });
      return data;
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Erro desconhecido";
      setState({ data: null, loading: false, error: message });
      throw err;
    }
  }, []);

  return { ...state, refetch };
}
