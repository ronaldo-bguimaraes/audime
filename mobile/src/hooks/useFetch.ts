import { useState, useEffect, useCallback } from "react"

type UseFetchResult<T> = {
  data: T | null
  error: string | null
  isLoading: boolean
  refetch: () => void
}

export function useFetch<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = [],
): UseFetchResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await fetcher()
      setData(result)
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Erro inesperado"
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }, deps)

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, error, isLoading, refetch: fetchData }
}
